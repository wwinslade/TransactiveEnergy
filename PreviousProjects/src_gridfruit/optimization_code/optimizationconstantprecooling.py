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
    #m.setParam('NonConvex', 2)
    m.setParam('MIPGap', 0.1)
    m.setParam('Timelimit', 60*60)

    #these parameters were found by looking for times it took to go from 2.22-4.44 respectively
    #short cycle time is still 600 seconds, so that will be our sampletime

    Loadmass=12000#grams of water between 0 and 16000, curve fitting done at 0, 8k, and 16k
    #times have been modified to evenly divide by the short cycle time, the comments give the original time and percent diff with the in-use value
    medtimetocool=10800#10815 sec, 0.138%
    medtimetoheat=5400# 5325, 1.38% seconds taken to go from 2.22 to 4.44 C
    fulltimetocool=16200# 15930, 1.66%
    fulltimetoheat=15600# 15810, 1.34%
    medthermostatenergy=7#W-hr of energy per hour
    fullthermostatenergy=6.25# W-hr of energy per hour
    interptimetocool=medtimetocool + (Loadmass-8000)*(fulltimetocool-medtimetocool)/(8000)
    interptimetoheat=medtimetoheat + (Loadmass-8000)*(fulltimetoheat-medtimetoheat)/(8000)
    interpthermostatenergy=medthermostatenergy + (Loadmass-8000)*(fullthermostatenergy-medthermostatenergy)/(8000)
    
    sampletime=600#seconds, the 
    #### need to insert additional data for every ten minute interval into pricing data
    unmodifiedlength=len(PriceDateTimes)
    Prices=[]
    Times=[]
    for i in range(24):#can alter the range to get shorter time periods, e.x 
        for j in range(int(3600/sampletime)):#add in additional timeslots based on short cycle time length
            Prices.append(DAprices[i])
            Times.append(PriceDateTimes[i]+dt.timedelta(seconds=j*sampletime))
        
    relaxed = False
    if relaxed:
        vartype=GRB.CONTINUOUS
    else:
        vartype=GRB.BINARY

    ##normal variables
    p=m.addVars(range(0,len(Times)), vtype=vartype,lb=0,ub=1, name="compressorstate")#should the compressor be on or off, amount of variables is total seconds in year divide by short cycle time.
    T=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtemp")
    
    
    ##Auxiliary variables
    ## Gurobi can only do constraints with power<=2, but we can decompose terms with greater powers into smaller ones by using auxiliary variables to represent the smaller powers.
    ## Alternatively, we can use power constraints to define a variable y, equal to x^a where a is constant, approximated via a piecewise linear function.
    ## Using either of these methods, we can replace the high power terms in the curve fit equations. These are general auxiliary variables, interpolation specific ones are below
    tmed=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="temperaturemedium")
    tfull=m.addVars(range(0,len(Times)), vtype=GRB.CONTINUOUS, name="temperaturefull")
    #T2=m.addVars(range(0,(len(Times)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtempsquared")
    
    '''
    linear curve fits
    Cooling time in temp out
    no load: y = -0.0411x + 4.8767  R² = 0.9039
    med load: y = -0.0016x + 3.9974  R² = 0.9188
    full load: y = -0.0013x + 4.3475 R² = 0.9418

    cooling temp in time out
    no load: y = -344.29x + 1714.1  R² = 0.9911
    med load: y = -8491.1x + 35613  R² = 0.9218
    full load: y = -10959x + 49223  R² = 0.9443

    heating time in temp out
    no load: y = 0.0016x + 0.1949  R² = 0.9622
    med load: y = 0.0004x + 1.1036 R² = 0.8804
    full load:y = 0.0002x + 0.4295 R² = 0.9886

    heating temp in time out
    no load: y = 589.12x - 54.44 R² = 0.9622
    med load: y = 2025.3x - 1615.2 R² = 0.8804
    full load: y = 6577x - 2640.5 R² = 0.9886
    '''

    #build constraints 
    for i in range(0,len(Times)):
        m.addConstr((p[i]==0)>>(tmed[i]==T[i] + 0.0004*Shortcycletime))#temp in time out med load heaitng
        m.addConstr((p[i]==1)>>(tmed[i]==T[i] -0.0016*Shortcycletime))#temp in time out med load cooling
        m.addConstr((p[i]==0)>>(tfull[i]==T[i] +0.0002*Shortcycletime))#temp in time out med load heaitng
        m.addConstr((p[i]==1)>>(tfull[i]==T[i] -0.0013*Shortcycletime))#temp in time out med load cooling
        m.addConstr((T[i+1]==tmed[i] + (Loadmass-8000)*(tfull[i]-tmed[i])/(8000)),"interptemp")#heating medium load

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
    m.setObjective(gp.quicksum(Prices[i]*p[i]*1/6*3.8*10**-5 for i in range(0,len(Times))), GRB.MINIMIZE)
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