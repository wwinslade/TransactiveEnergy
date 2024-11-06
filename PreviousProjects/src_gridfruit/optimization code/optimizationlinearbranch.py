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

with open('rt_hrl_lmps.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    RTprices=[]
    for row in reader:
        RTprices.append(row['total_lmp_rt']) #$/MWh

#basic parameters
Hightempboundary=5#degrees celsius, max is 22C
Lowtempboundary=1#degrees celsius, min is 0C
Loadmass=8000#grams of water between 0 and 16000, curve fitting done at 0, 8k, and 16k
Shortcycletime=600#seconds, minimum amount of time that must occur between on-off cycles to prevent short cycling. Minimum amount of time compressor can be in one state

##### Convert entries in PriceDatetimes to dates and times
format="%m/%d/%y %I:%M %p" #these are the utc time
PriceDateTimes=[]
for i in range(len(Pricedt)):
    #time=dt.datetime.strptime(Pricedt[i], "%m/%d/%y %H:%M %p")
    #time2=dt.datetime.strftime(time,)
    PriceDateTimes.append(dt.datetime.strptime(Pricedt[i], format))
unmodifiedlength=len(PriceDateTimes)

#determine standard thermostat performance at given loadmass via interpolation
def standard_performance(filename,daprices):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        testpower=[]
        times=[]
        for row in reader:
            testpower.append(float(row['power'])) #$/MWh
            times.append(row['datetime'])
    
    format="%m/%d/%Y %H:%M" #these are the utc time
    powertimes=[]
    for i in range(len(times)):
    #time=dt.datetime.strptime(Pricedt[i], "%m/%d/%y %H:%M %p")
    #time2=dt.datetime.strftime(time,)
        powertimes.append(dt.datetime.strptime(times[i], format))
            
            
    for i in range(len(testpower)):
        if testpower[i]<=0:
            testpower[i]=0
        else:
            testpower[i]=testpower[i]
    unmodifiedcostyear=0
    unmodifiedcostdaily=[]
    for k in range(365):
        dailypricesset=daprices[k*24:k*24+24]
        unmodifieddailyprices=[]#prices to be used for calculating cost for oem thermostat operation
        for i in range(24):#can alter the range to get shorter time periods, e.x 
            for j in range(int(3600/120)):#ubibot reads every 2 minutes
                unmodifieddailyprices.append(dailypricesset[i])
        unmodifiedcostyear=unmodifiedcostyear+sum(float(unmodifieddailyprices[i])*testpower[i]*1/30*10**-6 for i in range(len(unmodifieddailyprices)))
        unmodifiedcostdaily.append(sum(float(unmodifieddailyprices[i])*testpower[i]*1/30*10**-6 for i in range(len(unmodifieddailyprices))))
        output={"dailycost":unmodifiedcostdaily,"yearlycost":unmodifiedcostyear,"testpower":testpower,"powertimes":powertimes}
    return output

#standardnoload=standard_performance('thermostatnoloadpower.csv',RTprices)
standardfull=standard_performance('thermostatfullloadpower.csv',RTprices)
standardmed=standard_performance('thermostathalfloadpower.csv',RTprices)

dailycoststandard=[]
if Loadmass>=8000:
    for i in range(len(standardfull["dailycost"])):
        dailycoststandard.append(standardmed["dailycost"][i] + (Loadmass-8000)*(standardfull["dailycost"][i]-standardmed["dailycost"][i])/(8000))
else:
    for i in range(len(standardmed["dailycost"])):
        dailycoststandard.append(standardnoload["dailycost"][i] + (Loadmass-8000)*(standardmed["dailycost"][i]-standardnoload["dailycost"][i])/(8000))
yearlycoststandard=sum(dailycoststandard)








#Intelligent scheduling optimization
##### Parameter set-up
compstates=[]
temperature=[]
schedulechange=[]
totalenergy=0#amount of energy used over entire year in Wh
totalcostDA=0
totalcostRT=0
try:
    #### need to insert additional data for every ten minute interval into pricing data
    unmodifiedlength=len(PriceDateTimes)
    m=gp.Model()
    #m.setParam('NonConvex', 2)
    m.setParam('MIPGap', 0.1)
    m.setParam('Timelimit', 60*60)
    dailyenergyDA=[]
    dailycostDA=[]
    dailycostRT=[]
    graphday=1 #what iteration (k-value) of the optimization to print graphs for
    for k in range(365):
        dailypricessetDA=DAprices[k*24:k*24+24]
        dailypricessetRT=RTprices[k*24:k*24+24]
        dailytimesset=PriceDateTimes[k*24:k*24+24]
        dailypricesDA=[]
        dailypricesRT=[]
        dailytimes=[]
        for i in range(24):#can alter the range to get shorter time periods, e.x 
            for j in range(int(3600/Shortcycletime)):#add in additional timeslots based on short cycle time length
                dailypricesDA.append(dailypricessetDA[i])#prices just for the current day
                dailypricesRT.append(dailypricessetRT[i])#prices just for the current day
                dailytimes.append(dailytimesset[i]+dt.timedelta(seconds=j*Shortcycletime))#times just for the current day
        relaxed = False
        if relaxed:
            vartype=GRB.CONTINUOUS
        else:
            vartype=GRB.BINARY

        '''
        linear curve fits 0 C to 5C
        Cooling time in temp out
        no load: y = -0.0411x + 4.8767 R² = 0.9039
        med load: y = -0.0016x + 3.9974 R² = 0.9188
        full load: y = -0.0013x + 4.3475 R² = 0.9418

        heating time in temp out
        no load: y = 0.0016x + 0.1949 R² = 0.9622
        med load: y = 0.0004x + 1.1054 R² = 0.8803
        full load: y = 0.0002x + 0.4274 R² = 0.9886
        '''
        if k==0:
        #build constraints
            p=m.addVars(range(0,len(dailytimes)), vtype=vartype,lb=0,ub=1, name="p")#should the compressor be on or off, amount of variables is total seconds in year divide by short cycle time.
            T=m.addVars(range(0,(len(dailytimes)+1)), vtype=GRB.CONTINUOUS, name="T")
            tlow=m.addVars(range(0,len(dailytimes)), vtype=GRB.CONTINUOUS, name="tlow")
            tmed=m.addVars(range(0,len(dailytimes)), vtype=GRB.CONTINUOUS, name="tmed")
            tfull=m.addVars(range(0,len(dailytimes)), vtype=GRB.CONTINUOUS, name="tfull")
            Desiredtemp=3#degrees celsius, 37.4 f
            for i in range(0,len(dailytimes)):
                m.addConstr((p[i]==0)>>(tlow[i]==T[i] + 0.0016*Shortcycletime))#temp in time out med load heaitng
                m.addConstr((p[i]==1)>>(tlow[i]==T[i] -0.0411*Shortcycletime))#temp in time out med load cooling
                m.addConstr((p[i]==0)>>(tmed[i]==T[i] + 0.0004*Shortcycletime))#temp in time out med load heaitng
                m.addConstr((p[i]==1)>>(tmed[i]==T[i] -0.0016*Shortcycletime))#temp in time out med load cooling
                m.addConstr((p[i]==0)>>(tfull[i]==T[i] +0.0002*Shortcycletime))#temp in time out med load heaitng
                m.addConstr((p[i]==1)>>(tfull[i]==T[i] -0.0013*Shortcycletime))#temp in time out med load cooling
                if Loadmass>=8000:
                    m.addConstr((T[i+1]==tmed[i] + (Loadmass-8000)*(tfull[i]-tmed[i])/(8000)),"interptemphigh")#heating medium load
                else:
                    m.addConstr((T[i+1]==tlow[i] + (Loadmass-0)*(tmed[i]-tlow[i])/(8000)),"interptemplow")#heating medium load

            m.addConstrs((T[i]>=Lowtempboundary for i in range(0,(len(dailytimes)+1))), "Tlowererbound")
            m.addConstrs((T[i]<=Hightempboundary for i in range(0,(len(dailytimes)+1))), "Tupperbound")
            m.addConstr((T[0]==Desiredtemp), 'initialtemp')
            #m.addConstrs((T[i+1]==Nexttempmed[i]+(Loadmass-8000)*(Nexttempnf[i]-Nexttempmed[i])/(8000) for i in range(0,len(Times))), "Futuretemp")
        else:
            m.remove(m.getConstrs()[-1])
            m.addConstr((T[0]==temps[-1]), 'initialtemp')
        #average power use is 33 watts
        m.setObjective(gp.quicksum(dailypricesDA[i]*p[i]*Shortcycletime/3600*3.3*10**-5 for i in range(0,len(dailytimes))), GRB.MINIMIZE)
        #m.feasRelaxS(0,True,True,False)
        m.optimize()
        m.write('optimization.lp')
    
        #v.obj is the objective function coeffecient for the variable, RC is reduced cost, then SAOBjup and low are the allowable range
        comp=[]
        temps=[]
        for i in range(len(dailytimes)):
            comp.append(p[i].X)
            temps.append(T[i].X)
        comp=np.asarray(list(map(float, comp)))
        temps=np.asarray(list(map(float, temps)))
        compstates.append(comp)
        temperature.append(temps)
        dailyenergyDA.append(np.sum(comp)*Shortcycletime/3600*33)
        dailycostDA.append(m.objval)
        dailycostRT.append(np.sum(float(dailypricesRT[i])*comp[i]*Shortcycletime/3600*3.3*10**-5 for i in range(0,len(dailytimes))))
        totalenergy=totalenergy+np.sum(comp)*Shortcycletime/3600*33
        totalcostDA=totalcostDA+m.objval
        totalcostRT=totalcostRT+dailycostRT[k]
        if k==0:
            schedule=list(map(float, comp))
        else:
            schedulechange.append(schedule==list(map(float, comp)))
            schedule=list(map(float, comp))

        # print optimal objective value
        print('Obj: %g' % m.ObjVal)
        print('daily energy use is: %g :watt hours' % dailyenergyDA[k])
        print('total cost: %g' %totalcostDA)
        print('total energy: %g' %totalenergy)
        # print optimal value of variables
        print('Solution, reduced costs, ranges')
        m.reset()
        m.update()
    
        ##### plotting results
        def createplot(type,standardcase,k,graphday):
            fig, axs=plt.subplots()#plots for price over time, temp over time, comp state over time, and then price and compstate in the same figure
            if k==graphday:
                if type==1:
                    axs.set_title("price over time")
                    axs.plot(dailytimes, np.asarray(list(map(float, dailypricesDA))))
                    axs.set_xlabel("day and hour")
                    axs.set_ylabel("price in $/MWh")
                elif type==2:
                    axs.set_title("Temp over time")
                    axs.plot(dailytimes, temps)
                    axs.set_xlabel("day and hour")
                    axs.set_ylabel("Temperature in $^\circ$C")
                elif type==3:
                    axs.set_title('compressor state over time')
                    axs.plot(dailytimes, comp)
                    axs.set_xlabel("day and hour")
                    axs.set_ylabel("Compressor on/off")
                elif type==4:
                    axs.set_title('Price versus compressor state')
                    line1,=axs.plot(dailytimes,np.asarray(list(map(float, dailypricesDA))),color="green", label="DA price")
                    ax2=axs.twinx()
                    line2,=ax2.plot(dailytimes,comp, label="compressor state")
                    axs.set_xlabel("Day and hour")
                    axs.set_ylabel("price in $/MWh")
                    ax2.set_ylabel('Compressor on/off')
                    axs.legend(handles=[line1,line2])
                elif type==5:
                    axs.set_title('Baseline power usage')
                    axs.plot(standardcase["powertimes"],np.asarray(standardcase["testpower"]), color="orange")
                    axs.set_xlabel('Day and hour')
                    axs.set_ylabel('Power consumption in watts')
                else:
                    axs.set_title('Temperature versus compressor state')
                    line1,=axs.plot(dailytimes,temps,color="red",label='temperature')
                    ax2=axs.twinx()
                    line2,=ax2.plot(dailytimes,comp,label="compressor state")
                    axs.set_xlabel("Day and hour")
                    axs.set_ylabel("Temperature in ($^\circ$C)")
                    ax2.set_ylabel('Compressor on/off')
                    axs.legend(handles=[line1,line2])
            else:
                pass
        createplot(3,standardfull)
except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')

print('end')