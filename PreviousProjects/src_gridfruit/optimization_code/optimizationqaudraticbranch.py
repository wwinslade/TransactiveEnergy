import xlrd
import pprint
import gurobipy as gp
from gurobipy import GRB
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import datetime as dt
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
format="%m/%d/%y %I:%M %p" #these are the utc time
PriceDateTimes=[]
for i in range(len(Pricedt)):
    #time=dt.datetime.strptime(Pricedt[i], "%m/%d/%y %H:%M %p")
    #time2=dt.datetime.strftime(time,)
    PriceDateTimes.append(dt.datetime.strptime(Pricedt[i], format))



totaltime=dt.timedelta.total_seconds(PriceDateTimes[-1]-PriceDateTimes[0])
##### Parameter set-up
try:

    m=gp.Model("GFsavings")
    m.setParam('NonConvex', 2)
    m.setParam('MIPGap', 0.1)
    m.setParam('Timelimit', 60*60)

    Hightempboundary=4.44#degrees celsius, max is 22C
    Lowtempboundary=2.22#degrees celsius, min is 0C
    Desiredtemp=3.33#degrees celsius, 38 f
    Loadmass=12000#grams of water between 0 and 16000, curve fitting done at 0, 8k, and 16k
    Shortcycletime=600#seconds, minimum amount of time that must occur between on-off cycles to prevent short cycling. Minimum amount of time compressor can be in one state

    #### need to insert additional data for every ten minute interval into pricing data
    unmodifiedlength=len(PriceDateTimes)
    Prices=[]
    Times=[]
    for i in range(5):#can alter the range to get shorter time periods, e.x 
        for j in range(int(3600/Shortcycletime)):#add in additional timeslots based on short cycle time length
            Prices.append(DAprices[i])
            Times.append(PriceDateTimes[i]+dt.timedelta(seconds=j*Shortcycletime))
        
    relaxed = False
    if relaxed:
        vartype=GRB.CONTINUOUS
    else:
        vartype=GRB.BINARY

    ##normal variables
    p=m.addVars(range(0,len(Times)), vtype=vartype,lb=0,ub=1, name="compressorstate")#should the compressor be on or off, amount of variables is total seconds in year divide by short cycle time.
    T=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtemp")
    #tmed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="medium time")#time to reach current temp from zero for the medium load curve
    #tfull=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="full time")#time to reach current temp from zero for the full load curve
    
    ##Auxiliary variables
    ## Gurobi can only do constraints with power<=2, but we can decompose terms with greater powers into smaller ones by using auxiliary variables to represent the smaller powers.
    ## Alternatively, we can use power constraints to define a variable y, equal to x^a where a is constant, approximated via a piecewise linear function.
    ## Using either of these methods, we can replace the high power terms in the curve fit equations. These are general auxiliary variables, interpolation specific ones are below
    tempmed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="temperaturemedium")
    tempfull=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="temperaturefull")
    #T2=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtempsquared")
    
    '''
    curve fit equations
    Cooling time in temp out
    med load: y = 3E-09x2 - 0.0002x + 4.8211  R² = 0.993
    full load: y = 1E-09x2 - 0.0002x + 5.0673  R² = 0.9946

    cooling temp in time out
    med load: y = -8491.1x + 35613  R² = 0.9218
    full load: y = -10959x + 49223  R² = 0.9443

    heating time in temp out
    med load: y = -6E-08x2 + 0.001x + 0.0989  R² = 0.986
    full load: y = -2E-09x2 + 0.0002x + 0.1142  R² = 0.9986

    heating temp in time out
    med load: y = 2025.3x - 1615.2  R² = 0.8804
    full load: y = 6577x - 2640.5  R² = 0.9886
    '''

    #build constraints 
    for i in range(0,len(Times)):
        #m.addConstr((p[i]==0)>>(tmed[i]==2025.3*T[i]-1615.2))#temp in time out med load heaitng
        #m.addConstr((p[i]==1)>>(tmed[i]==-8491.1*T[i]+35613))#temp in time out med load cooling
        #m.addConstr((p[i]==0)>>(tfull[i]==6577*T[i]-2640.5))#temp in time out med load heaitng
        #m.addConstr((p[i]==1)>>(tfull[i]==-10959*T[i]+49223))#temp in time out med load cooling

        m.addConstr((p[i]==0)>>(tempmed[i]==T[i] + (2*-6*10**-8*(2025.3*T[i]-1615.2)+0.001)*Shortcycletime))#temp in time out med load heaitng
        m.addConstr((p[i]==1)>>(tempmed[i]==T[i] - (2*3*10**-9*(-8491.1*T[i]+35613)-0.0002)*Shortcycletime))#temp in time out med load cooling
        m.addConstr((p[i]==0)>>(tempfull[i]==T[i] + (2*-2*10**-9*(6577*T[i]-2640.5)+0.0002)*Shortcycletime))#temp in time out med load heaitng
        m.addConstr((p[i]==1)>>(tempfull[i]==T[i] - (2*1*10**-9*(-10959*T[i]+49223)-0.0002)*Shortcycletime))#temp in time out med load cooling
        m.addConstr((T[i+1]==tempmed[i] + (Loadmass-8000)*(tempfull[i]-tempmed[i])/(8000)),"interptemp")#heating medium load

    m.addConstrs((T[i]>=Lowtempboundary for i in range(0,(len(Times)+1))), "Tlowererbound")
    m.addConstrs((T[i]<=Hightempboundary for i in range(0,(len(Times)+1))), "Tupperbound")
    m.addConstr((T[0]==Desiredtemp), 'initial temp')
    #m.addConstrs((T[i+1]==Nexttempmed[i]+(Loadmass-8000)*(Nexttempnf[i]-Nexttempmed[i])/(8000) for i in range(0,len(Times))), "Futuretemp")


    #need constraint that will determine the next period of time based off previous period of time +temp increase or decrease as a function of amount of time compressor was on or off
    #we can test constant performance/baseline for the year by looking at baseline operation for a day and extending it across a year.
    #yes, you can use function in constraint definitions 
    
    #solve
    #m.setObjective(sum([Prices[i]*p[i] for i in range(0,len(Times))]), GRB.MINIMIZE) #divided by 6 since each time block is ten minutes and units is #/MWH hour, need to also scale it by actual power consumption and time step *1/6*3.8e-5
    #average power use is 38 watts
    m.setObjective(gp.quicksum(Prices[i]*p[i] for i in range(0,len(Times))), GRB.MINIMIZE)
    #m.feasRelaxS(0,True,True,False)
    m.optimize()
    #m.write('optimization.lp')
    compstates=[]
    temperature=[]
    #v.obj is the objective function coeffecient for the variable, RC is reduced cost, then SAOBjup and low are the allowable range
    for i in range(len(Times)):
        compstates.append(p[i].X)
        temperature.append(T[i].X)
    compstates=np.asarray(list(map(float, compstates)))
    temperature=np.asarray(list(map(float, temperature)))
    totalenergy=np.sum(compstates)*1/6*38


    # print optimal objective value
    print('Obj: %g' % m.ObjVal)
    print('Total energy use is: %g :watt hours' % totalenergy)
    # print optimal value of variables
    print('Solution, reduced costs, ranges')
   
    
##### plotting results
    fig, axs=plt.subplots(2,2)#plots for price over time, temp over time, comp state over time, and then price and compstate in the same figure
    axs[0,0].set_title("price over time")
    axs[0,0].plot(Times, np.asarray(list(map(float, Prices))))
    axs[0,1].set_title("Temp over time")
    axs[0,1].plot(Times, temperature)
    axs[1,0].set_title('compressor state over time')
    axs[1,0].plot(Times, compstates)
    axs[1,1].set_title('price versus compressor state')
    axs[1,1].plot(Times,np.asarray(list(map(float, Prices))))
    ax2=axs[1,1].twinx()
    ax2.plot(Times,compstates)
except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')

print('end')