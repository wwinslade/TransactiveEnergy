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
import matplotlib.dates as mdates

#### description
'''
two optimizations are ran. The baseline simulates normal thermostatic operation and seeks to minimize excursions from temperature band
Scheduling optimization seeks to minimize electricity cost based on DA prices
both use historical temperatures and pricing and simulate decrease and increases in refrigerated stock.
three levels of stock decrease are assumed 

savings are compared based on real-time prices
'''



#### global variables
Hightempboundary=5#degrees celsius, max is 22C
Lowtempboundary=1#degrees celsius, min is 0C
Shortcycletime=600#seconds, minimum amount of time that must occur between on-off cycles to prevent short cycling. Minimum amount of time compressor can be in one state

##calculating info for CoP values and whatnot
baselinecarnot=269.75/(285.59-269.75) #287 is average year round temp in athenia, 269.75 is cold side of evap, 285.59 is average yearly temp in contigous united states
''' this didn't work
specheatwater=4.15#kJ/(kg*K)
specheatair=1.006#kJ/(kg*k)
dT=5 #change in temperature
h20mass=[0,8000/1000,16000/1000]#grams
airmass=[1.2*0.09,1.2*(0.09-8/997),1.2*(0.09-16/997)]#assuming 1.2 kg/m^3 from engineering toolbox at 70F, 0.09 cubic meter fridge volume, mass of water/water density equal water volume
specheatcombined=[(specheatwater*h20mass[0]+specheatair*airmass[0])/(h20mass[0]+airmass[0]),(specheatwater*h20mass[1]+specheatair*airmass[1])/(h20mass[1]+airmass[1]),(specheatwater*h20mass[2]+specheatair*airmass[2])/(h20mass[2]+airmass[2])]
#work=[338,1728,2883]#kJ
work=[0.041,0.48,0.8]#kW-hr
heatremoved=[(h20mass[0]+airmass[0])*specheatcombined[0]*24,(h20mass[1]+airmass[1])*specheatcombined[1]*dT,(h20mass[2]+airmass[2])*specheatcombined[2]*dT]
CoP=[heatremoved[0]/work[0],heatremoved[1]/work[1],heatremoved[2]/work[2]]
'''
CoPbaseline=1.625#average value for commercial refrigeration from https://ieeexplore.ieee.org/document/7458465
syseta=CoPbaseline/baselinecarnot
qbaseline=CoPbaseline*38*3600#joules
#### reading in datasets
with open('da_hrl_lmpswithtemperature.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    Pricedt=[]
    DAprices=[]
    weather=[]#outside air temp in c
    for row in reader:
        DAprices.append(float(row['total_lmp_da'])) #$/MWh
        Pricedt.append(row['datetime_beginning_ept'])
        weather.append(float(row['temperature']))

with open('rt_hrl_lmpsarticle.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    RTprices=[]
    for row in reader:
        RTprices.append(float(row['total_lmp_rt'])) #$/MWh

format="%m/%d/%y %H:%M" #these are the utc time
PriceDT=[]
for i in range(len(Pricedt)):
    #time=dt.datetime.strptime(Pricedt[i], "%m/%d/%y %H:%M %p")
    #time2=dt.datetime.strftime(time,)
    PriceDT.append(dt.datetime.strptime(Pricedt[i], format))


#### functions
'''
linear curve fits 0 C to 5C
Cooling time in temp out
no load: y = -0.0029x + 4.9556 R² = 0.9911
med load: y = -0.0001x + 3.9998 R² = 0.9218
full load: y = -9E-05x + 4.3496 R² = 0.9443

heating time in temp out
no load: y = 0.0016x + 0.1949 R² = 0.9622
med load: y = 0.0004x + 1.1054 R² = 0.8803
full load: y = 0.0002x + 0.4274 R² = 0.9886
'''
def fullcurves(heatcool,currenttemp,timestep):
    if heatcool=='heat':
        nexttemp=currenttemp+timestep*0.0002
    else:
        nexttemp=currenttemp+timestep*-0.00009
    return nexttemp

def midcurves(heatcool,currenttemp,timestep):
    if heatcool=='heat':
        nexttemp=currenttemp+timestep*0.0004
    else:
        nexttemp=currenttemp+timestep*-0.0001
    return nexttemp

def nocurves(heatcool,currenttemp,timestep):
    if heatcool=='heat':
        nexttemp=currenttemp+timestep*0.0016
    else:
        nexttemp=currenttemp+timestep*-0.0029
    return nexttemp

def ctok(Tc):
    #converts C to kelvin
    Tk=Tc+273.15
    return Tk 

def ctof(Tc):
    #converts celsius to fahrenheit
    Tf=(Tc*9/5)+32
    return Tf

def ftoc(Tf):
    #convert fahrenheit to clesius
    Tc=(Tf-32)*5/9
    return Tc

def calcetachange(Th,Tc=''):
    #calculate efficiency lossed and gained over course of day by changing outside temperature (Th) effect on carnot efficiency and return required power for constant cooling rate of 171 kJ/hr
    if Tc=='':
        newpowerconsumptions=qbaseline/(syseta *ctok(-3.4)/(ctok(Th)-ctok(-3.4))*3600)#for linear formulation
        newcop=syseta*ctok(-3.4)/(ctok(Th)-ctok(-1.7))
    else:
        newpowerconsumptions=qbaseline/(syseta *ctok(Tc)/(ctok(Th)-ctok(Tc))*3600)#for linear formulation
        newcop=syseta*ctok(Tc)/(ctok(Th)-ctok(Tc))
    if newpowerconsumptions<=qbaseline/(baselinecarnot*3600):#this ensures that when temperature goes negative, system is still consuming power
        newpowerconsumptions=qbaseline/(baselinecarnot*3600)#for linear formulation
        newcop=baselinecarnot
    else:
        pass
    return newpowerconsumptions,newcop

def calculatestocklevels(endstock,timestep, constant=0):
    #calculates stock level schedule given lowest level of stock for the day.
    #Refrigerated stock will decrease linearly from 8-am to 10 PM and will then be restocked linearly from 10PM-12am, and resume restocking from 6 am-8am
    fullstock=16000#amount of grams for full refrigerated stock
    totaltime=24*60*60 #amount of seconds in a day
    stocklevels=np.zeros(int(totaltime/timestep)).tolist()
    indiceperhour=int(3600/timestep) #amount of timesteps per hour
    i8am=8*indiceperhour-1
    stocklevels[i8am]=fullstock
    i8pm=20*indiceperhour-1
    i10pm=22*indiceperhour-1
    i6am=6*indiceperhour-1
    decreaserate=np.linspace(fullstock,endstock,indiceperhour*12+1).tolist()[0]-np.linspace(fullstock,endstock,indiceperhour*12+1).tolist()[1]
    increaserate=np.linspace(endstock,fullstock,indiceperhour*6+1).tolist()[1]-np.linspace(endstock,fullstock,indiceperhour*6+1).tolist()[0]
    j=0
    for i in range(i8am,i8pm+1):#find linear decrease
        stocklevels[i]=int(fullstock-j*decreaserate)
        j=j+1
    j=0
    for i in range(i8pm,len(stocklevels)):
        if i==i8pm:
            pass
        else:
            stocklevels[i]=int(endstock+j*increaserate)
        j=j+1
    for i in range(0,i6am):
        stocklevels[i]=stocklevels[-1]
    j=0
    for i in range(i6am,i8am):
        stocklevels[i]=int(stocklevels[i-1]+increaserate)
        j=j+1
    for i in range(0,len(stocklevels)):
        if stocklevels[i]==16000:
            stocklevels[i]=15999
        elif stocklevels[i]==8000:
            stocklevels[i]=7999
        else:
            pass
    if constant==1:
        for i in range(0,len(stocklevels)):
            stocklevels[i]=endstock      
    return stocklevels

####thermostatic baseline simulation
def calcbaseline(Nadir,constantstock,PriceDT, DAprices, RTprices, weather, dispoutputs=1):#does either a baseline or optimal scheduling with varying stock nadirs
    schedulechange=[]
    totalenergy=0#amount of energy used over entire year in Wh
    totalcostDA=0
    totalcostRT=0
    outputdict={}
    stocklevels=calculatestocklevels(Nadir,Shortcycletime,constantstock)
    
    #### need to insert additional data for every ten minute interval into pricing data
    dailyenergy=[]
    dailycostDA=[]
    dailycostRT=[]
    for k in range(365):
        l=24
        m=24
        dailypricessetDA=DAprices[k*l:k*l+m]
        dailypricessetRT=RTprices[k*l:k*l+m]
        dailytimesset=PriceDT[k*l:k*l+m]
        dailyweatherset=weather[k*l:k*l+m]
        dailypricesDA=[]
        dailypricesRT=[]
        dailytimes=[]
        dailyweather=[]
        for i in range(l):#can alter the range to get shorter time periods, e.x 
            for j in range(int(3600/Shortcycletime)):#add in additional timeslots based on short cycle time length
                dailypricesDA.append(dailypricessetDA[i])#prices just for the current day
                dailypricesRT.append(dailypricessetRT[i])#prices just for the current day
                dailytimes.append(dailytimesset[i]+dt.timedelta(seconds=j*Shortcycletime))#times just for the current day
                dailyweather.append(dailyweatherset[i])

        comp=np.empty(len(dailytimes)).tolist()
        power=np.empty(len(dailytimes)).tolist()
        powerused=np.empty(len(dailytimes)).tolist()
        temps=np.empty(len(dailytimes)+1).tolist()
        if k==0:
            temps[0]=3#starting temp is 3C
        else:
            temps[0]=outputdict[(k-1)]['temps'][-1]#grab last temperature from previous day and set as starting temp
        for i in range(len(dailytimes)):
            if stocklevels[i]>=8000:#calculate what temps could be in next timestep
                theat=midcurves('heat',temps[i],Shortcycletime)+(stocklevels[i]-8000)*(fullcurves('heat',temps[i],Shortcycletime)-midcurves('heat',temps[i],Shortcycletime))/8000
                tcool=midcurves('cool',temps[i],Shortcycletime)+(stocklevels[i]-8000)*(fullcurves('cool',temps[i],Shortcycletime)-midcurves('cool',temps[i],Shortcycletime))/8000
            else:
                theat=nocurves('heat',temps[i],Shortcycletime)+(stocklevels[i])*(midcurves('heat',temps[i],Shortcycletime)-nocurves('heat',temps[i],Shortcycletime))/8000
                tcool=nocurves('cool',temps[i],Shortcycletime)+(stocklevels[i])*(midcurves('cool',temps[i],Shortcycletime)-nocurves('cool',temps[i],Shortcycletime))/8000
            if k==0 and i==0:
                if theat>Hightempboundary:
                    temps[i+1]=tcool
                    comp[0]=1
                    power[0]=calcetachange(dailyweather[i])[0]
                    powerused[0]=comp[0]*calcetachange(dailyweather[i])[0]
                else:
                    temps[i+1]=theat
                    comp[0]=0
                    power[0]=calcetachange(dailyweather[i])[0]
                    powerused[0]=0
            elif k!=0 and i==0:
                if theat>Hightempboundary:
                    temps[i+1]=tcool
                    comp[i]=1
                    power[i]=calcetachange(dailyweather[i])[0]
                    powerused[i]=comp[i]*calcetachange(dailyweather[i])[0]
                else:
                    temps[i+1]=theat
                    comp[i]=0
                    power[i]=calcetachange(dailyweather[i])[0]
                    powerused[i]=0
            elif theat>Hightempboundary:
                temps[i+1]=tcool
                comp[i]=1
                power[i]=calcetachange(dailyweather[i])[0]
                powerused[i]=comp[i]*calcetachange(dailyweather[i])[0]
            elif tcool<Lowtempboundary:
                temps[i+1]=theat
                comp[i]=0
                power[i]=calcetachange(dailyweather[i])[0]
                powerused[i]=0
            elif (tcool>=Lowtempboundary and theat<=Hightempboundary) and comp[i-1]==0:
                temps[i+1]=theat
                comp[i]=0
                power[i]=calcetachange(dailyweather[i])[0]
                powerused[i]=0
            elif (tcool>=Lowtempboundary and theat<=Hightempboundary) and comp[i-1]==1:
                temps[i+1]=tcool
                comp[i]=1
                power[i]=calcetachange(dailyweather[i])[0]
                powerused[i]=comp[i]*calcetachange(dailyweather[i])[0]
            else:
                    print('you done churched it up, dirt')

        #v.obj is the objective function coeffecient for the variable, RC is reduced cost, then SAOBjup and low are the allowable range
        

        comp=np.asarray(list(map(int, comp)))
        temps=np.asarray(list(map(float, temps)))
        power=np.asarray(list(map(float, power)))
        powerused=np.asarray(list(map(float, powerused)))
        dailyenergy.append(np.sum(power[i]*comp[i]*Shortcycletime/3600 for i in range(0,len(dailytimes)))) #watt-hours
        dailycostDA.append(np.sum(float(dailypricesDA[i])*power[i]*comp[i]*Shortcycletime/3600*10**-5 for i in range(0,len(dailytimes))))
        dailycostRT.append(np.sum(float(dailypricesRT[i])*power[i]*comp[i]*Shortcycletime/3600*10**-5 for i in range(0,len(dailytimes))))
        totalenergy=totalenergy+dailyenergy[k]
        totalcostDA=totalcostDA+dailycostDA[k]
        totalcostRT=totalcostRT+dailycostRT[k]
        peakpowerused=np.max(powerused)
        if k==0:
            schedule=list(map(int, comp))
        else:
            schedulechange.append(schedule==list(map(int, comp)))
            schedule=list(map(int, comp))
        placeholderdict={"compstates":comp,"temps":temps,"powers":power,"powerused":powerused,"peakpower":peakpowerused,"energy":dailyenergy,"DAcost":dailycostDA,"RTcost":dailycostRT, "Datetimes":dailytimes, "DAprices":dailypricesDA,"RTprices":dailypricesRT, "Dailyweather":np.asarray(list(map(int, dailyweather)))}
        indice=k
        outputdict.update({indice:placeholderdict})
        # print optimal objective value
        if dispoutputs==1:
            print('daily electricity cost is: %g $'  % dailycostRT[k])
            print('daily energy use is: %g watt hours' % dailyenergy[k])
            print('total costDA: %g $ ' %totalcostDA)
            print('total costRT: %g $ ' %totalcostRT)
            print('total energy: %g watt hours' %totalenergy)
        else:
            pass
    outputdict.update({"totalenergy":totalenergy,"totalcostDA":totalcostDA,"totalcostRT":totalcostRT})   

    return outputdict


#### MILP schedule solver
def findoptschedules(Nadir,constantstock,PriceDT, DAprices, RTprices, weather, dispoutputs=1):
    schedulechange=[]
    totalenergy=0#amount of energy used over entire year in Wh
    totalcostDA=0
    totalcostRT=0
    outputdict={}
    stocklevels=calculatestocklevels(Nadir,Shortcycletime,constantstock)
    
    #### need to insert additional data for every ten minute interval into pricing data
    dailyenergy=[]
    dailycostDA=[]
    dailycostRT=[]
    for k in range(365):
        dailypricessetDA=DAprices[k*24:k*24+24]
        dailypricessetRT=RTprices[k*24:k*24+24]
        dailytimesset=PriceDT[k*24:k*24+24]
        dailyweatherset=weather[k*24:k*24+24]
        dailypricesDA=[]
        dailypricesRT=[]
        dailytimes=[]
        dailyweather=[]
        for i in range(24):#can alter the range to get shorter time periods, e.x 
            for j in range(int(3600/Shortcycletime)):#add in additional timeslots based on short cycle time length
                dailypricesDA.append(dailypricessetDA[i])#prices just for the current day
                dailypricesRT.append(dailypricessetRT[i])#prices just for the current day
                dailytimes.append(dailytimesset[i]+dt.timedelta(seconds=j*Shortcycletime))#times just for the current day
                dailyweather.append(dailyweatherset[i])

        powerconsumption=np.empty(len(dailytimes)).tolist()
        m=gp.Model()
        #m.setParam('NonConvex', 2)
        m.setParam('MIPGap', 0.1)
        m.setParam('Timelimit', 60*60)
        vartype=GRB.BINARY
        
        #build constraints
        p=m.addVars(range(0,len(dailytimes)), vtype=vartype,lb=0,ub=1, name="p")#should the compressor be on or off, amount of variables is total seconds in year divide by short cycle time.
        T=m.addVars(range(0,(len(dailytimes)+1)), vtype=GRB.CONTINUOUS, name="interpolatedtemp")
        tmed=m.addVars(range(0,len(dailytimes)), vtype=GRB.CONTINUOUS, name="tmed")
        talt=m.addVars(range(0,len(dailytimes)), vtype=GRB.CONTINUOUS, name="talt")
        Desiredtemp=3#degrees celsius, 37.4 f
        for i in range(0,len(dailytimes)):
            powerconsumption[i]=calcetachange(dailyweather[i])[0]
            m.addConstr((p[i]==0)>>(tmed[i]==T[i] + 0.0004*Shortcycletime),name='medloadheating')#medloadheating
            m.addConstr((p[i]==1)>>(tmed[i]==T[i] -0.0001*Shortcycletime),name='medloadcooling')#medloadcooling
            if stocklevels[i]>=8000:
                m.addConstr((p[i]==0)>>(talt[i]==T[i] +0.0002*Shortcycletime), name='fulloadheating')#fullloadheating
                m.addConstr((p[i]==1)>>(talt[i]==T[i] -0.00009*Shortcycletime),name='fulloadcooling')#fullloadcooling
                m.addConstr((T[i+1]==tmed[i] + (stocklevels[i]-8000)*(talt[i]-tmed[i])/(8000)),name="interptempupper")#heating medium load
            else:
                m.addConstr((p[i]==0)>>(talt[i]==T[i] + 0.0016*Shortcycletime),name='noloadheating')#noloadheating
                m.addConstr((p[i]==1)>>(talt[i]==T[i] -0.0029*Shortcycletime),name='noloadcooling')#noloadcooling
                m.addConstr((T[i+1]==talt[i] + (stocklevels[i]-0)*(tmed[i]-talt[i])/(8000)),name="interptemplower")#heating medium load

        m.addConstrs((T[i]>=Lowtempboundary for i in range(0,(len(dailytimes)+1))), "Tlowererbound")
        m.addConstrs((T[i]<=Hightempboundary for i in range(0,(len(dailytimes)+1))), "Tupperbound")
        if k==0:
            m.addConstr((T[0]==Desiredtemp), 'initialtemp')
        else:
            m.addConstr((T[0]==temps[-1]), 'initialtemp')
        m.setObjective(gp.quicksum(p[i]*dailypricesDA[i]*powerconsumption[i]*Shortcycletime/3600*10**-5 for i in range(0,len(dailytimes))), GRB.MINIMIZE)
        #m.feasRelaxS(0,True,True,False)
        m.optimize()
        #m.write('optimization.lp')

        ### writing to output dictionary
        comp=[]
        temps=[]
        power=[]
        powerused=[]
        for i in range(0,len(dailytimes)):
            comp.append(int(p[i].X))
            temps.append(T[i].X)
            power.append(powerconsumption[i])
            powerused.append(power[i]*comp[i])
        comp=np.asarray(list(map(int, comp)))
        temps=np.asarray(list(map(float, temps)))
        power=np.asarray(list(map(float, power)))
        powerused=np.asarray(list(map(float, powerused)))
        dailyenergy.append(np.sum(power[i]*comp[i]*Shortcycletime/3600 for i in range(0,len(dailytimes)))) #watt-hours
        dailycostDA.append(np.sum(float(dailypricesDA[i])*power[i]*comp[i]*Shortcycletime/3600*10**-5 for i in range(0,len(dailytimes))))
        dailycostRT.append(np.sum(float(dailypricesRT[i])*power[i]*comp[i]*Shortcycletime/3600*10**-5 for i in range(0,len(dailytimes))))
        totalenergy=totalenergy+dailyenergy[k]
        totalcostDA=totalcostDA+dailycostDA[k]
        totalcostRT=totalcostRT+dailycostRT[k]
        peakpowerused=np.max(powerused)
        if k==0:
            schedule=list(map(int, comp))
        else:
            schedulechange.append(schedule==list(map(int, comp)))
            schedule=list(map(int, comp))
        placeholderdict={"compstates":comp,"temps":temps,"powers":power,"powerused":powerused,"peakpower":peakpowerused,"energy":dailyenergy,"DAcost":dailycostDA,"RTcost":dailycostRT, "Datetimes":dailytimes, "DAprices":dailypricesDA,"RTprices":dailypricesRT, "Dailyweather":np.asarray(list(map(int, dailyweather)))}
        indice=k
        outputdict.update({indice:placeholderdict})
        # print optimal objective value
        if dispoutputs==1:
            print('daily electricity cost is: %g $'  % dailycostRT[k])
            print('daily energy use is: %g watt hours' % dailyenergy[k])
            print('total costDA: %g $ ' %totalcostDA)
            print('total costRT: %g $ ' %totalcostRT)
            print('total energy: %g watt hours' %totalenergy)
        else:
            pass
    outputdict.update({"totalenergy":totalenergy,"totalcostDA":totalcostDA,"totalcostRT":totalcostRT})   

    return outputdict

####graphing function
def createplot(type,dict,graphday):
    fig, axs=plt.subplots()#plots for price over time, temp over time, comp state over time, and then price and compstate in the same figure
    if type==1:
        axs.set_title("Day-Ahead LMP Over Time")
        axs.plot(dict[graphday]['Datetimes'], dict[graphday]['DAprices'])
        axs.set_xlabel("Day and Hour")
        axs.set_ylabel("price in $/MWh")
    elif type==2:
        axs.set_title("Refrigerator Temperature Over Time")
        axs.plot(dict[graphday]['Datetimes'], dict[graphday]['temps'][0:144])
        axs.set_xlabel("Day and Hour")
        axs.set_ylabel("Temperature in $^\circ$C")
    elif type==3:
        axs.set_title('Compressor State Over Time')
        axs.plot(dict[graphday]['Datetimes'], dict[graphday]['compstates'])
        axs.set_xlabel("day and hour")
        axs.set_ylabel("Compressor on/off")
    elif type==4:
        axs.set_title('LMP Versus Compressor State')
        line1,=axs.plot(dict[graphday]['Datetimes'], dict[graphday]['DAprices'],color="green", label="DA Price")
        ax2=axs.twinx()
        line2,=ax2.plot(dict[graphday]['Datetimes'],dict[graphday]['compstates'], label="Compressor State")
        axs.set_xlabel("Day and Hour")
        axs.set_ylabel("price in $/MWh")
        ax2.set_ylabel('Compressor on/off')
        axs.legend(handles=[line1,line2])
    elif type==5:
        axs.set_title('Compressor Power Versus Exterior Temperature')
        line1,=axs.plot(dict[graphday]['Datetimes'],dict[graphday]['powers'],color="green", label="Compressor Power")
        ax2=axs.twinx()
        line2,=ax2.plot(dict[graphday]['Datetimes'],dict[graphday]['Dailyweather'], label="Exterior Temperature")
        axs.set_xlabel("Day and Hour")
        axs.set_ylabel("Compressor power in watts")
        ax2.set_ylabel('Exterior temperature in ($^\circ$C)')
        axs.legend(handles=[line1,line2])
    elif type==6:
        axs.set_title('Refrigerator Temperature Versus Compressor State')
        line1,=axs.plot(dict[graphday]['Datetimes'],dict[graphday]['temps'],color="red",label='Interior Temperature')
        ax2=axs.twinx()
        line2,=ax2.plot(dict[graphday]['Datetimes'],dict[graphday]['compstates'],label="compressor state")
        axs.set_xlabel("Day and Hour")
        axs.set_ylabel("Interior Temperature in ($^\circ$C)")
        ax2.set_ylabel('Compressor on/off')
        axs.legend(handles=[line1,line2])
    elif type==7:
        axs.set_title('Refrigerator Temperature Versus Compressor State')
    elif type==8:
        axs.set_title("Refrigerated Stock Levels over 24-hours",fontsize=50)
        axs.tick_params(labelsize=20)
        hours=[]
        for i in range(len(dict[graphday]['Datetimes'])):
            hours.append(dict[graphday]['Datetimes'][i].hour)
        axs.plot(dict[graphday]['Datetimes'][0:144],stocklevels['16000'],color="red",label='16000')
        axs.plot(dict[graphday]['Datetimes'][0:144],stocklevels['12000'],color="blue",label='12000')
        axs.plot(dict[graphday]['Datetimes'][0:144],stocklevels['8000'],color="green",label='8000')
        axs.plot(dict[graphday]['Datetimes'][0:144],stocklevels['4000'],color="brown",label='4000')
        axs.plot(dict[graphday]['Datetimes'][0:144],stocklevels['0'],color="black",label='0')
        axs.set_xlabel("Hour of the day",fontsize=40)
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        axs.set_ylabel("Stock level in grams",fontsize=40)
        axs.legend(title='Stock Level Nadir', fontsize=40, title_fontsize=40)

        
    else:
        pass
   

#### analysis functions
def percentdiff(new, old):
    return (new-old)/old

def yearlyaverages(outputdict,key):
    a=[]
    for i in range(0,365):
        a.append(outputdict[i][key])
    a=np.asarray(a)
    return np.mean(a)

def yearlypeak(outputdict,key):
    a=[]
    for i in range(0,365):
        a.append(outputdict[i][key])
    a=np.asarray(a)
    return np.max(a)

def averagedailypeak(outputdict,key):
    a=[]
    for i in range(0,365):
        a.append(outputdict[i][key])
    a=np.asarray(a)
    return np.mean(a)

def summarizerun(outputdict, title):
    print('results for '+ title)
    print('total costDA: %g $ ' %outputdict['totalcostDA'])
    print('total costRT: %g $ ' %outputdict['totalcostRT'])
    print('total energy: %g watt hours' %outputdict['totalenergy'])
    print('peak power used for year: %g watts' %yearlypeak(outputdict,'peakpower'))
    print('average daily DA cost is: %g $'  % yearlyaverages(outputdict,'DAcost'))
    print('average daily RT cost is: %g $'  % yearlyaverages(outputdict,'RTcost'))
    print('average daily energy use is: %g Watt hours'  % yearlyaverages(outputdict,'energy'))
    print('average daily peak power is: %g watts' % averagedailypeak(outputdict, 'peakpower'))
    print('')

def dicttoexcel(dict, filename):
    df = pd.DataFrame(data=dict)
    df = (df.T)
    df.to_excel(filename)   

stocklevels={'16000':calculatestocklevels(16000,600),'12000':calculatestocklevels(12000,600),'8000':calculatestocklevels(8000,600),'4000':calculatestocklevels(4000,600),'0':calculatestocklevels(0,600)}
#### baseline performance
therm16000const=calcbaseline(16000,1,PriceDT,DAprices,RTprices,weather,0)
therm12000const=calcbaseline(12000,1,PriceDT,DAprices,RTprices,weather,0)
therm8000const=calcbaseline(8000,1,PriceDT,DAprices,RTprices,weather,0)
therm4000const=calcbaseline(4000,1,PriceDT,DAprices,RTprices,weather,0)
therm0const=calcbaseline(0,1,PriceDT,DAprices,RTprices,weather,0)
therm16000var=calcbaseline(16000,0,PriceDT,DAprices,RTprices,weather,0)
therm12000var=calcbaseline(12000,0,PriceDT,DAprices,RTprices,weather,0)
therm8000var=calcbaseline(8000,0,PriceDT,DAprices,RTprices,weather,0)
therm4000var=calcbaseline(4000,0,PriceDT,DAprices,RTprices,weather,0)
therm0var=calcbaseline(0,0,PriceDT,DAprices,RTprices,weather,0)
baselinetempprofiles={'16000':therm16000var[8]['temps'],'12000':therm12000var[8]['temps'],'8000':therm8000var[8]['temps'],'4000':therm4000var[8]['temps'],'0':therm0var[8]['temps']}
#### optimized performance
opt16000const=findoptschedules(16000,1,PriceDT,DAprices,RTprices,weather,0)
opt12000const=findoptschedules(12000,1,PriceDT,DAprices,RTprices,weather,0)
opt8000const=findoptschedules(8000,1,PriceDT,DAprices,RTprices,weather,0)
opt4000const=findoptschedules(4000,1,PriceDT,DAprices,RTprices,weather,0)
opt0const=findoptschedules(0,1,PriceDT,DAprices,RTprices,weather,0)
opt16000var=findoptschedules(16000,0,PriceDT,DAprices,RTprices,weather,0)
opt12000var=findoptschedules(12000,0,PriceDT,DAprices,RTprices,weather,0)
opt8000var=findoptschedules(8000,0,PriceDT,DAprices,RTprices,weather,0)
opt4000var=findoptschedules(4000,0,PriceDT,DAprices,RTprices,weather,0)
opt0var=findoptschedules(0,0,PriceDT,DAprices,RTprices,weather,0)



#### calculating results


#### results analysis


#createplot(3,base12000,8)
results=[therm16000const,therm12000const,therm8000const,therm4000const,therm0const,therm16000var,therm12000var,therm8000var,therm4000var,therm0var,opt16000const,opt12000const,opt8000const,opt4000const,opt0const,opt16000var,opt12000var,opt8000var,opt4000var,opt0var]
titles=['therm16000const','therm12000const','therm8000const','therm4000const','therm0const','therm16000var','therm12000var','therm8000var','therm4000const','therm0var','opt16000const','opt12000const','opt8000const','opt4000const','opt0const','opt16000var','opt12000var','opt8000var','opt4000var','opt0var']
for i in range(len(results)):
    summarizerun(results[i],titles[i])
print('end for real')


