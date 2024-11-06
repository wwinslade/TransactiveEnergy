import xlrd
import pprint
import gurobipy as gp
from gurobipy import GRB
import itertools
import pandas as pd
import csv
import datetime as dt
import numpy as np
from gurobipy import GRB


###### Pull in hourly price data for the year

with open('da_hrl_lmps.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    Pricedt=[]
    DAprices=[]
    for row in reader:
        DAprices.append(row['total_lmp_da']) #$/MWh
        Pricedt.append(row['datetime_beginning_utc'])

##### Convert entries in PriceDatetimes to dates and times
format="%m/%d/%Y %H:%M:%S %p" #these are the utc time
PriceDateTimes=[]
for i in range(len(Pricedt)):
    PriceDateTimes.append(dt.datetime.strptime(Pricedt[i], format))



totaltime=dt.timedelta.total_seconds(PriceDateTimes[-1]-PriceDateTimes[0])
##### Parameter set-up
m=gp.Model("GFsavings")
m.setParam('NonConvex', 2)
#m.setParam('MIPGap', 0.1)
m.setParam('Timelimit', 60*60)
#m.params.NonConvex = 2 #comment in if doing lp-relaxation

Hightempboundary=4.44#degrees celsius, max is 22C
Lowtempboundary=2.22#degrees celsius, min is 0C
Desiredtemp=3.33#degrees celsius, 38 f
Loadmass=12000#grams of water between 0 and 16000, curve fitting done at 0, 8k, and 16k
Shortcycletime=600#seconds, minimum amount of time that must occur between on-off cycles to prevent short cycling. Minimum amount of time compressor can be in one state

#### need to insert additional data for every ten minute interval into pricing data
unmodifiedlength=len(PriceDateTimes)
Prices=[]
Times=[]
for i in range(0,2):#can alter the range to get shorter time periods, e.x 
    for j in range(int(3600/Shortcycletime)):#add in additional timeslots based on short cycle time length
        Prices.append(DAprices[i])
        Times.append(PriceDateTimes[i]+dt.timedelta(seconds=j*Shortcycletime))
    
relaxed = False
if relaxed:
    vartype=GRB.CONTINUOUS
else:
    vartype=GRB.BINARY
try:
    ##normal variables
    p=m.addVars(range(0,len(Times)), vtype=vartype,lb=0,ub=1, name="compressor state")#should the compressor be on or off, amount of variables is total seconds in year divide by short cycle time.
    Nexttemplu=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="predictedtemplowerupper")
    Nexttempmed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="predictedtempmed")
    T=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtemp")
    
    ##Auxiliary variables
    ## Gurobi can only do constraints with power<=2, but we can decompose terms with greater powers into smaller ones by using auxiliary variables to represent the smaller powers.
    ## Alternatively, we can use power constraints to define a variable y, equal to x^a where a is constant, approximated via a piecewise linear function.
    ## Using either of these methods, we can replace the high power terms in the curve fit equations. These are general auxiliary variables, interpolation specific ones are below

    #temperature
    temp2=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="temp^2")
    temp3=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="temp^3")
    temp4=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="temp^4")
    for i in range(0,(len(Times)+1)):
        m.addGenConstrPow(T[i],temp2[i],2)
        m.addGenConstrPow(T[i],temp3[i],3)
        m.addGenConstrPow(T[i],temp4[i],4)

    htimemed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimemed")
    htimemed2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimemed^2")
    ctimemed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimemed")
    ctimemed2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimemed^2")
    ctimemed3=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimemed^3")
    ctimemed4=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimemed^4")
    ctimemed5=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimemed^5")

    m.addConstrs((htimemed[i]==291.94*temp2[i] - 692.49*T[i] + 6705 + Shortcycletime for i in range(0,len(Times))))
    m.addConstrs((ctimemed[i]==-1.4173*temp4[i] - 66.641*temp3[i] + 1214.5*temp2[i] - 12632*T[i] + 72062+ Shortcycletime for i in range(0,len(Times))))
    for i in range(0,len(Times)):
        m.addGenConstrPow(htimemed[i],htimemed2[i],2)
        m.addGenConstrPow(ctimemed[i],ctimemed2[i],2)
        m.addGenConstrPow(ctimemed[i],ctimemed3[i],3)
        m.addGenConstrPow(ctimemed[i],ctimemed4[i],4)
        m.addGenConstrPow(ctimemed[i],ctimemed5[i],5)
    m.addConstrs(((p[i]==0)>>(Nexttempmed[i]==-9e-10*htimemed2[i] + 0.0003*htimemed[i] + 2.3445) for i in range(0,len(Times))),"medmasstemp")#heating
    m.addConstrs(((p[i]==1)>>(Nexttempmed[i]==-2e-22*ctimemed5[i]+4e-17*ctimemed4[i]-3e-12*ctimemed3[i]+1e-7*ctimemed2[i]-0.0018*ctimemed[i]+21.526) for i in range(0,len(Times))),"medmasstemp")#cooling
    m.addConstrs((T[i]>=Lowtempboundary for i in range(0,(len(Times)+1))), "Tlowererbound")
    m.addConstrs((T[i]<=Hightempboundary for i in range(0,(len(Times)+1))), "Tupperbound")
    m.addConstr((T[0]==Desiredtemp), 'initial temp')
    #### set objective function
    m.setObjective(sum([Prices[i]*p[i] for i in range(0,len(Times))]), GRB.MINIMIZE) #divided by 6 since each time block is ten minutes and units is #/MWH hour, need to also scale it by actual power consumption and time step *1/6*3.8e-5

    
    if Loadmass>0 and Loadmass<8000:### schedule assuming load is between no and medium load conditions
    ##### add additional variables for interpolation
        htimelow=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimelow")
        htimelow2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimelow^2")
        ctimelow=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimelow")
        ctimelow2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimelow^2")
        
    #### build constraints 
        m.addConstrs((htimelow[i]==0.6306*temp4[i]-22.295*temp3[i] + 245.64*temp2[i] - 43.156*T[i] + 1061.1 + Shortcycletime for i in range(0,(len(Times)+1))))
        m.addConstrs((ctimelow[i]==5.0545*temp2[i] - 327.08*T[i] + 4958 + Shortcycletime for i in range(0,(len(Times)+1))))
        for i in range(0,(len(Times)+1)):
            m.addGenConstrPow(htimelow[i],htimelow2[i],2)
            m.addGenConstrPow(ctimelow[i],ctimelow2[i],2)
        m.addConstrs(((p[i]==0)>>(Nexttemplu[i]== -3e-8*htimelow2[i] + 0.0017*htimelow[i] - 2.0997) for i in range(0,len(Times))),"medmasstemp")#heating
        m.addConstrs(((p[i]==1)>>(Nexttemplu[i]== 5e-7*ctimelow2[i]-0.0068*ctimelow[i]+22.787) for i in range(0,len(Times))),"medmasstemp")#cooling
        m.addConstrs((T[i+1]==Nexttemplu[i]+(Loadmass-0)*(Nexttempmed[i]-Nexttemplu[i])/(8000) for i in range(0,len(Times))), "Futuretemp")

    else: #### schedule assuming load is between medium and full load conditions
        ##### add additional variables for interpolation
        htimefull=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimefull")
        htimefull2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="htimefull^2")
        ctimefull=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimefull")
        ctimefull2=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="ctimefull^2")
        #build constraints 
        m.addConstrs((htimefull[i]==99.057*temp2[i]+8701.1*T[i]-8309.8 +Shortcycletime for i in range(0,len(Times))))
        m.addConstrs((ctimefull[i]==-17.245*temp3[i] + 752.47*temp2[i] - 13388*T[i] + 101000 +Shortcycletime for i in range(0,len(Times))))
        for i in range(0,len(Times)):
            m.addGenConstrPow(htimefull[i],htimefull2[i],2)
            m.addGenConstrPow(ctimefull[i],ctimefull2[i],2)
        m.addConstrs(((p[i]==0)>>(Nexttemplu[i]== -7e-11*htimefull2[i]+0.0001*htimefull[i]+1.0776) for i in range(0,len(Times))),"medmasstemp")#heating
        m.addConstrs(((p[i]==1)>>(Nexttemplu[i]== 4e-7*ctimefull2[i]-0.0052*ctimefull[i]+18.248) for i in range(0,len(Times))),"medmasstemp")#cooling
        m.addConstrs((T[i+1]==Nexttempmed[i]+(Loadmass-8000)*(Nexttemplu[i]-Nexttempmed[i])/(8000) for i in range(0,len(Times))), "Futuretemp")
   

    #need constraint that will determine the next period of time based off previous period of time +temp increase or decrease as a function of amount of time compressor was on or off
    #we can test constant performance/baseline for the year by looking at baseline operation for a day and extending it across a year.
    #yes, you can use function in constraint definitions 
     #solve

    m.optimize()
    #m.write('optimization.lp')

    # print optimal objective value
    print('Obj: %g' % m.ObjVal)

    # print optimal value of variables
    print('Solution, reduced costs, ranges')
    #v.obj is the objective function coeffecient for the variable, RC is reduced cost, then SAOBjup and low are the allowable range
    for v in m.getVars():
        print('%s %g' % (v.VarName, v.X))

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')

print('end')