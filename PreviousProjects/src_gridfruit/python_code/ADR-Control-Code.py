from ast import Pass
import logging
from pickle import TRUE
import sys
import random
import matplotlib
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
import matplotlib.pyplot as plt
import threading
import time
import pandas as pd
import datetime
import Interpcalc
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
#########################  General comments and information
#TBD, will fill out as more stuff is added

## Plan for general structure
#Use threads, process, etc to replicate how labview has multiple loops running simultaneously
#Process/threads will share inputs and outputs

#settings input loop
#contains declaration of variables that will be used by multiple threads or should be
#changeable on the fly. Have a way to enter inputs from terminal to change variable values
#will have to read certain inputs from sql database


#Daq loop
#handles temp sensing. Log's to an excel file and exports temp to other loops and sql database

##XML loop
#Needs to extract ADR info from xml loop

#Control loop
#takes temp data and parameters from input and daq loops, does control logic and spits out
#command to relay api

#output loop
#displays temp and other system states visually. At most basic, just needs to be a plot
#of temp and compressor status


########################## Initial settings

#default values of various settings
#these are contained within a dictionary so control locks for threading only have to keep track of one variable when writing


#logicals
#logtrue, log temperature data to an excel file
#usewebcontrol, read information from sql database for certain settings written from website
#useinterpprecool, use interpolation based-precooling
#overrideautomation, ignore automation output in favor of direct setting of compressor status
#enableADR, use certain values pulled out of from ADR xml file to control system

#Logging
#samplerate, controls how often the daq process iterates, 

#temp controls
#Hightempboundary, temp above which system automatically turns compressor on
#Lowtempboundary, temp below which system automatically turns compressor off
#desiredtemp, temp we want to reach and maintain
#loadmass, mass of load in grams
#precoolingminutes,time before event starts to begin pre-cooling if interpolative pre-cooling isn't used

settings={"logtrue":1,
"useinterpprecool":1,
"overrideautomation":0,
"enableADR":1,
"samplerate":15,
"Hightempboundary":15,
"Lowtempboundary":5,
"desiredtemp":10,
"loadmass":200,
"readtemp":1,
"precoolingstart":datetime.datetime.strptime("3/7/2022 11:30:00","%m/%d/%Y %H:%M:%S"),
"event start":datetime.datetime.strptime("3/7/2022 12:30:00","%m/%d/%Y %H:%M:%S"), #format code for strptime is %m/%d/%Y %H:%M:%S
"event end":datetime.datetime.strptime("3/7/2022 13:30:00","%m/%d/%Y %H:%M:%S")
}

varcurrent={"Datetime":datetime.datetime.now(),"Internal air temp":20,
"External air temp":20,"Evaporator temp":20,"Interior surface temp":20,"Compressor status":20,
"Precoolstart":datetime.datetime.now()+datetime.timedelta(hours=5),"Interptemp":15}#current values of system variables

########################## Process definitions

#Settigns input processes
#allow for changing of default setting values from terminal while code runs
def input_loop():
    statement=input()
    eval(statement)
    #input automatically converts whatever is entered to a string. eval takes only strings as inputs
    #inputs to eval must be expressions or function calls. Exec allows you to change variable values
    #exec("a['b']=4") for example if inputted to the input loop, statement would equal "exec("a['b']=4")"
    #this gets thrown into eval with then changes the value of b in dictionary a to 4 (a doesn't exist,
    # it's just an example). exec("settings['Hightempboundary']=10") is a more pertinent example 
    

# DAQ process
#pulls info from sensors, optionally logs it to an excel file, and then sends temp info to other processes
def DAQ_loop():

    with nidaqmx.Task(new_task_name="temperature sensing and logging") as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0:3")
        task.timing.cfg_samp_clk_timing(10, sample_mode=AcquisitionType.CONTINUOUS)
        getstructtime=time.localtime()
        while settings["readtemp"]==1:
            tempdata=task.read() #reads in temperature data from DAQ
            readdatetime=datetime.datetime.now()#records day last temp reading was made
            time.sleep(settings["samplerate"]) # delays iteration of sampling loop to limit sampling rate
            print('iter')

def append_dict(dictname,keyname,appendvalue):
    #appends value to dictionary entry if said entry is a list
    a=dictname[keyname]
    a.append(appendvalue)
    dictname[keyname]=a
    return(dictname)

def Logging_loop(currentvar):
    #takes current variable data, appends it to historical log, and then optionally saves log as an excel file
    #need to append all current data so each list is same length in dictionary before converting to dataframe
    varlog={"Datetime":[],"Internal air temp":[],"External air temp":[],"Evaporator temp":[],
    "Interior surface temp":[],"Compressor status":[],"Precoolstart":[],"Interptemp":[]}
    a=1
    while a==1:
        varkeys=list(currentvar.keys())
        for i in len(varkeys):
            varlog=append_dict(varlog,varkeys(i),currentvar[varkeys[i]])
        varxl=pd.DataFrame(varlog)#converts to pandas dataframe to write to excel
        if settings["logtrue"]==1:
            varxl.to_excel('./testsys.xlsx')#writing to excel overwrites the old file, doesn't append or open a new copy

def XML_loop():
    pass

def Control_loop():
    a=1
    if settings["overrideautomation"]==1:
        pass#just want to set compressor status directly via input loop
    else:
        while a==1:
            if settings["enableADR"]==0:
                ##normal deadband for adr not enabled
                if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                else:
                    while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                        varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
               
            ## deadbands for adr enabled
            else:
                if datetime.datetime.now()<=settings["event end"] and datetime.datetime.now()>=settings["event start"]:#keep temp just slightly below high temp for duration of event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    else:
                        while varcurrent["Internal air temp"]>=settings["Hightempboundary"]-2:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
            
                elif datetime.datetime.now()>settings["event end"]:#normal deadband for post event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
               
                elif datetime.datetime.now()>settings["precoolingstart"] and datetime.datetime.now()<settings["event start"]:
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    elif settings["useinterpprecool"]==1:
                        while varcurrent["Internal air temp"]>=varcurrent["Interptemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below the temp meant to interpolate to
                    else:
                        while varcurrent["Internal air temp"]>=settings["Lowtempboundary"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                 



                else:# prior to pre-cooling, normal deadband
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-1:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                    

def Output_loop():
    pass

def interpolation_loop():
    
    eventseconds=datetime.timedelta.total_seconds(settings["event end"]-settings["event start"])#length of event in seconds
    [timeneededtocool,temptocoolto]=Interpcalc.interpolate(settings["Hightempboundary"],varcurrent["Internal air temp"],settings["event start"],settings["event end"],settings["loadmass"])
    if settings["useinterpprecool"]==1:
        varcurrent["Interptemp"]=temptocoolto
        #varcurrent["Precoolstart"]=settings[]
    else:
        pass


#initializing everything before threading
factory=PiGPIOFactory(host='160.36.59.241')
red=gpiozero.LED(24,pin_factory=factory)
# while True:
#     red.on()
#     time.sleep(1)
#     red.off()
#     time.sleep(1)


print('end')
