from ast import Pass
from asyncio import start_server
from asyncore import loop
import logging
from pickle import TRUE
from re import A, X
import sys
import random
from tkinter import Y
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
import threading
import time
import pandas as pd
import datetime as dt
import InterpcalcV2
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import XMLextraction
import time
import requests
import json


lock=threading.Lock()
waitforfill=threading.Event()
#########################  General comments and information
#TBD, will fill out as more stuff is added


settings={"logtrue":1,"precooltype":2,"overrideautomation":0,"enableADR":1,"samplerate":15,
        "Hightempboundary":5,"Lowtempboundary":3,"desiredtemp":4,"loadmass":16000,"readtemp":1,
        "precoolingtime":dt.timedelta(hours=1),"precoolingtemp":1,"overridecompstatus":1,
        "event start":0, #format code for strptime is %m/%d/%Y %H:%M:%S
        "event end":0,"logfilepath":'./testsys.csv',"UseXMLevent":0, "XMLfilepath":'./CPPpayload.txt'}

varcurrent={"Datetime":[],"Internal air temp":[],
            "Load temp":[],"Evaporator temp":[],"Interior surface temp":[],"Compressor status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[],'fallbackstart':[]}   
varlog={"Datetime":[],"Internal air temp":[],
            "Load temp":[],"Evaporator temp":[],"Interior surface temp":[],"Compressor status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[],'fallbackstart':[]}

factory=PiGPIOFactory(host='160.36.59.241')
comppin=gpiozero.LED(23,pin_factory=factory,active_high=False)#compressor pin
sigpin=gpiozero.LED(15,pin_factory=factory)#thermostat pin
sigpin.off()


#settings["event end"][1]

########################## Process definitions

# DAQ process
#pulls info from sensors, optionally logs it to an excel file, and then sends temp info to other processes
def get_temp():
    # Retrieves temp through Ubibot API and ubibot wifi thermometer
    # API Documentation https://www.ubibot.com/platform-api/1232/quick-start/
    account_key = "54183910b6a04fd59648e022d58a1229"
    channel = "42895"
    API_link = str("https://api.ubibot.com/channels/%s?account_key=%s"%(channel, account_key))
    API_response = requests.get(API_link).json()

    Json = json.loads(API_response["channel"]["last_values"])
    tempdata = np.array(Json["field1"]["value"])
    readdatetime=dt.datetime.now()#records day last temp reading was made
    return [tempdata,readdatetime]  

def DAQacquire():
    # Reads temp from thermo-couples using NiDAQMX
    with nidaqmx.Task(new_task_name="temperature sensing and logging") as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0:3")
        task.timing.cfg_samp_clk_timing(10, sample_mode=AcquisitionType.CONTINUOUS)
        getstructtime=time.localtime()
        tempdata=np.array(task.read()) #reads in temperature data from DAQ
        tempdata=(tempdata-1.25)/0.005+1
        readdatetime=dt.datetime.now()#records day last temp reading was made
    return [tempdata,readdatetime]    

def append_dict(dictname,keyname,appendvalue):
    #appends value to dictionary entry if said entry is a list
    a=dictname[keyname]
    a.append(appendvalue)
    dictname[keyname]=a
    return(dictname)

def Logthis(currentvar):
    global varlog
    global settings
    #takes current variable data, appends it to historical log, and then optionally saves log as an excel file
    #need to append all current data so each list is same length in dictionary before converting to dataframe
    
    varkeys=list(currentvar.keys())
    for i in range(len(varkeys)):
        varlog=append_dict(varlog,varkeys[i],currentvar[varkeys[i]])
    varxl=pd.DataFrame(varlog)#converts to pandas dataframe to write to excel
    if settings["logtrue"]==1:
        varxl.to_csv(settings["logfilepath"])#writing to excel overwrites the old file, doesn't append or open a new copy

def XML_loop():
    pass


def findcurrentevent(starts,ends,readtime):
    numofevents=len(starts)   
    #find what current event start and end should be
    index=np.searchsorted(starts,readtime)
    if index<numofevents:
        currentstart=starts[index]
        currentend=ends[index]
    else:
        currentstart=starts[numofevents-1]
        currentend=ends[numofevents-1]

    #find whether current time is pre,during, or post event

    if readtime<=currentstart:
        status='pre'
    elif readtime>=currentend:
        status='post'
    else:
        status='during'

    eventspan=currentend-currentstart
    return [currentstart, currentend,eventspan,status]


def logging_loop():
    global settings
    global varcurrent
    global lock
    global comppin
    i=0
    while 1:
        
        
        lock.acquire()
        #[tempdata,readdatetime]=get_temp() #uncomment to use ubibot thermometer
        [tempdata,readdatetime]=DAQacquire()
        if settings["UseXMLevent"]==1:
            [currentstart,duration]=XMLextraction.extractxmldates(settings["XMLfilepath"])
            currentend=currentstart+duration
            settings["event start"]=currentstart;settings["event end"]=currentend
        else:
            date=dt.datetime.today()
            event1start=dt.datetime(date.year,date.month,date.day,12)
            event1end=dt.datetime(date.year,date.month,date.day,20)

            eventstarts=[event1start]#comment this line out to do winter stuff
            eventends=[event1end]#comment this line out to do winter stuff

            #event2start=dt.datetime(date.year,date.month,date.day,12) #comment the next 4 lines in
            #event2end=dt.datetime(date.year,date.month,date.day,20)
            #eventstarts=[event1start,event2start]
            #eventends=[event1end,event2end]

            settings["event start"]=eventstarts;settings["event end"]=eventends

        [currentstart, currentend,eventspan,status]=findcurrentevent(settings["event start"],settings["event end"],readdatetime)
        timeneededtocool=InterpcalcV2.interpolate(settings["Lowtempboundary"],tempdata[1],currentstart,settings["loadmass"])
        timeneededtocool=dt.timedelta(seconds=timeneededtocool)

        #update varcurrent with temp data stuff
        if currentstart-timeneededtocool<currentstart:
            prestart=currentstart-timeneededtocool
            varcurrent["fallbackstart"]=prestart
        elif currentstart-timeneededtocool>currentstart and varcurrent["fallbackstart"]!=[]:
            prestart=varcurrent["fallbackstart"]
        else:
            varcurrent["fallbackstart"]=currentstart-dt.timedelta(hours=1)

        if settings["precooltype"]==2:#initial set-up of current variables, use interp precool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]=prestart
            varcurrent["Precooltemp"]=settings["precoolingtemp"];varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status#current values of system variables
        elif settings["precooltype"]==1:#update current variables, manually set pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]=currentstart-settings["precoolingtime"]
            varcurrent["Precooltemp"]=settings["precoolingtemp"];varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status#current values of system variables
        else:#no pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]= readdatetime
            varcurrent["Precooltemp"]=0;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status#current values of system variables
    
        lock.release()
       

        # if varcurrent["Compressor status"]==1:
        #     comppin.on()
        #     print('compon\n')
        # else:
        #     comppin.off()
        #     print('compoff')
        Logthis(varcurrent)
        time.sleep(settings["samplerate"]) # delays iteration of sampling loop to limit sampling rate
        waitforfill.set()
    
def control_loop():
    global settings
    global varcurrent
    global waitforfill
    global comppin
    l=waitforfill.wait()
    while 1:
        if settings["overrideautomation"]==1:
            if settings["overridecompstatus"]==0:
                comppin.off()
                varcurrent["Compressor status"]=0
            else:
                comppin.on()
                varcurrent["Compressor status"]=1
        else:
            if settings["enableADR"]==0:
                ##normal deadband for adr not enabled
                #lock.acquire()
                if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    comppin.off()
                    print('inbounds\n')
                elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    comppin.off()
                    print('below bounds \n')
                else:
                    while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                        varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                        comppin.on()
                        time.sleep(settings["samplerate"])
                        print('control loop compressor on while loop\n')
            ## deadbands for adr enabled
            else:
                if varcurrent["event status"]=="during":#keep temp just slightly below high temp for duration of event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                    else:
                        while varcurrent["Internal air temp"]>=settings["Hightempboundary"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()
                            time.sleep(settings["samplerate"])

                elif varcurrent["event status"]=='post':#normal deadband for post event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()                  
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()
                            time.sleep(settings["samplerate"])

                elif varcurrent['Datetime']>varcurrent['Precoolstart'] and varcurrent['event status']=='pre':
                    #if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                    #    varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    #    comppin.off()
                    if varcurrent["Internal air temp"]<settings["precoolingtemp"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                    else:
                        while varcurrent["Internal air temp"]>=settings["precoolingtemp"]:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()
                            print('pre-cooling active')
                            time.sleep(settings["samplerate"])

                else:# prior to pre-cooling, normal deadband
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()                    
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on() 
                            time.sleep(settings["samplerate"])
                #lock.release()
        time.sleep(settings["samplerate"])                       

def output_loop():
    global settings
    global varcurrent
    global waitforfill
    while 1:
        l=waitforfill.wait()
        print('compressor:',varcurrent["Compressor status"], 'air temp:',varcurrent["Internal air temp"], 'precooltemp:',varcurrent["Precooltemp"], '\n')
        print('event status:',varcurrent["event status"],"precool start:",varcurrent["Precoolstart"],'event start:',varcurrent["event start"],'event end:',varcurrent["event end"], '\n')
        time.sleep(settings["samplerate"])
    

def signal_loop():
    global sigpin
    global settings
    i=0
    while 1:
        if i%2==0:
            sigpin.off()
        else:
            sigpin.on()
        i=i+1
        time.sleep(settings["samplerate"])

## beginning threads
loggingloop=threading.Thread(target=logging_loop,args=[])
controlloop=threading.Thread(target=control_loop,args=[])
outputloop=threading.Thread(target=output_loop,args=[])
signalloop=threading.Thread(target=signal_loop,args=[])


loggingloop.start()
controlloop.start()
outputloop.start()
signalloop.start()

print('end')
