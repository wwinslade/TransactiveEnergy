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
import datetime
import Interpcalc
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import xml.etree.ElementTree as ET
lock=threading.Lock()
waitforfill=threading.Event()
#########################  General comments and information
#TBD, will fill out as more stuff is added

event1start=readdatetime=datetime.datetime.now()+datetime.timedelta(hours=1)
event2start=readdatetime=datetime.datetime.now()+datetime.timedelta(hours=4)

event1end=readdatetime=datetime.datetime.now()+datetime.timedelta(hours=2)
event2end=readdatetime=datetime.datetime.now()+datetime.timedelta(hours=5)

eventstarts=[event1start,event2start]
eventends=[event1end,event2end]

settings={"logtrue":1,"precooltype":0,"overrideautomation":0,"enableADR":0,"samplerate":15,
        "Hightempboundary":5,"Lowtempboundary":3,"desiredtemp":4,"loadmass":0,"readtemp":1,
        "precoolingtime":datetime.timedelta(hours=1),"overridecompstatus":1,
        "event start":eventstarts, #format code for strptime is %m/%d/%Y %H:%M:%S
        "event end":eventends,"logfilepath":'./testsys.xlsx'}

varcurrent={"Datetime":[],"Internal air temp":[],
            "Load temp":[],"Evaporator temp":[],"Interior surface temp":[],"Compressor status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[]}   
varlog={"Datetime":[],"Internal air temp":[],
            "Load temp":[],"Evaporator temp":[],"Interior surface temp":[],"Compressor status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[]}

factory=PiGPIOFactory(host='160.36.59.241')
comppin=gpiozero.LED(23,pin_factory=factory,active_high=False)#compressor pin
sigpin=gpiozero.LED(15,pin_factory=factory)#thermostat pin
sigpin.off()


#settings["event end"][1]

########################## Process definitions

# DAQ process
#pulls info from sensors, optionally logs it to an excel file, and then sends temp info to other processes
def DAQacquire():

    with nidaqmx.Task(new_task_name="temperature sensing and logging") as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0:3")
        task.timing.cfg_samp_clk_timing(10, sample_mode=AcquisitionType.CONTINUOUS)
        getstructtime=time.localtime()
        tempdata=np.array(task.read()) #reads in temperature data from DAQ
        tempdata=(tempdata-1.25)/0.005+1
        readdatetime=datetime.datetime.now()#records day last temp reading was made
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
        varxl.to_excel(settings["logfilepath"])#writing to excel overwrites the old file, doesn't append or open a new copy

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
        [tempdata,readdatetime]=DAQacquire()
        [currentstart, currentend,eventspan,status]=findcurrentevent(settings["event start"],settings["event end"],readdatetime)
        [timeneededtocool,temptocoolto]=Interpcalc.interpolate(settings["Hightempboundary"],tempdata[0],currentstart,currentend,settings["loadmass"])
        timeneededtocool=datetime.timedelta(seconds=timeneededtocool)

        #update varcurrent with temp data stuff
        if settings["precooltype"]==2:#initial set-up of current variables, use interp precool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]=currentstart-timeneededtocool
            varcurrent["Precooltemp"]=temptocoolto;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status#current values of system variables
        elif settings["precooltype"]==1:#update current variables, manually set pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]=currentstart-settings["precoolingtime"]
            varcurrent["Precooltemp"]=temptocoolto;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status#current values of system variables
        else:#no pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Load temp"]=tempdata[3]
            varcurrent["Evaporator temp"]=tempdata[0];varcurrent["Interior surface temp"]=tempdata[2];varcurrent["Precoolstart"]= readdatetime
            varcurrent["Precooltemp"]=temptocoolto;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
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
                        while varcurrent["Internal air temp"]>=settings["Hightempboundary"]-2:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()

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

                elif varcurrent['Datetime']>varcurrent['Precoolstart'] and varcurrent['event status']=='pre':
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                    elif settings["useinterpprecool"]==1:
                        while varcurrent["Internal air temp"]>=varcurrent["Interptemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below the temp meant to interpolate to
                            comppin.on()
                    else:
                        while varcurrent["Internal air temp"]>=settings["Lowtempboundary"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()

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
                #lock.release()
        time.sleep(settings["samplerate"])                       

def output_loop():
    global settings
    global varcurrent
    global waitforfill
    while 1:
        l=waitforfill.wait()
        print('compressor:',varcurrent["Compressor status"], 'air temp:',varcurrent["Internal air temp"], 'precooltemp:',varcurrent["Precooltemp"], '\n')
        print('event status:',varcurrent["event status"],'event start:',varcurrent["event start"],'event end:',varcurrent["event end"], '\n')
        time.sleep(settings["samplerate"])
    

def signal_loop():
    global sigpin
    global settings
    i=0
    while 1:
        if i%2==0:
            sigpin.off()
            print(0)
        else:
            sigpin.on()
            print(1)
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
