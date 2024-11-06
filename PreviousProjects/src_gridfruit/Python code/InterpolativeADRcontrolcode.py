# importing packages
#from asyncore import loop probably dont need this
import sys
import numpy as np
import threading
import time
import pandas as pd
import datetime as dt
import InterpcalcV4
import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import XMLextraction
import time
import requests
import json

#declaring concurrency tools
lock=threading.Lock()
waitforfill=threading.Event()


# Global variable declarations
settings={"logtrue":1,"precooltype":0,"operationmode":2,"enableADR":0,"samplerate":15,
        "Hightempboundary":6,"Lowtempboundary":0,"desiredtemp":3.3,"dbandoffset":0, "loadmass":4000,
        "precoolingtime":dt.timedelta(hours=1),"precoolingtemp":1,"overridecompstatus":0,
        "event start":0, #format code for strptime is %m/%d/%Y %H:%M:%S
        "event end":0,"logfilepath":'./testsys.csv',"UseXMLevent":0, "XMLfilepath":'./CPPpayload.txt'}
#operation modes are direct compressor control(0), thermostat only(1), digital logic only(2), and hybrid(3)

varcurrent={"Datetime":[],"Internal air temp":[],"Compressor status":[],"deadband status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[],'fallbackstart':[],'thermpin':[]}   

varlog={"Datetime":[],"Internal air temp":[],"Compressor status":[],"deadband status":[],
            "Precoolstart":[],"Precooltemp":[],"event start":[],"event end":[], "event status":[],'fallbackstart':[],'thermpin':[]}


#pin declarations
factory=PiGPIOFactory(host='160.36.59.241')
comppin=gpiozero.LED(23,pin_factory=factory,active_high=False)#compressor pin
sigpin=gpiozero.LED(15,pin_factory=factory)#signaling pin
sigpin.off()


##################################################### DAQ Process definitions
#functions to pull info from sensors, log it, and then figure out where we are in the timeline

def get_temp(targettemp):
    # Retrieves temp through Ubibot API and ubibot wifi thermometer
    # API Documentation https://www.ubibot.com/platform-api/1232/quick-start/
    account_key = "54183910b6a04fd59648e022d58a1229"
    channel = "42895"
    API_link = str("http://api.ubibot.com/channels/%s/?account_key=%s"%(channel, account_key))
    tempdata=np.array([0.0,0.0,0.0,0.0])
    try:
        API_response = requests.get(API_link).json()
        Json = json.loads(API_response["channel"]["last_values"])
        tempdata[1] =Json["field1"]["value"]
    except (requests.ConnectionError, requests.ConnectTimeout, requests.HTTPError,KeyError):    
        #If errors occur in reaching the API, just make temp slightly above target value and set to thermostat operation
        tempdata[1]=targettemp+1
        print('tempget exception occurred')
    readdatetime=dt.datetime.now()#records day last temp reading was made
    return [tempdata,readdatetime]  


'''
def DAQacquire():
    # Reads temp from thermo-couples using NiDAQMX, depraceted 
    with nidaqmx.Task(new_task_name="temperature sensing and logging") as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0:3")
        task.timing.cfg_samp_clk_timing(10, sample_mode=AcquisitionType.CONTINUOUS)
        getstructtime=time.localtime()
        tempdata=np.array(task.read()) #reads in temperature data from DAQ
        tempdata=(tempdata-1.25)/0.005+1
        readdatetime=dt.datetime.now()#records day last temp reading was made
    return [tempdata,readdatetime]    
'''
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
    varlog["Datetime"][-1]=varlog["Datetime"][-1].strftime('%x %X')
    varxl=pd.DataFrame(varlog)#converts to pandas dataframe to write to excel
    if settings["logtrue"]==1:
        varxl.to_csv(settings["logfilepath"])#writing to excel overwrites the old file, doesn't append or open a new copy

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


####################################################################loops

def logging_loop():
    #calls DAQ process functions to get temp, calculate pre-cooling time, update varcurrent with relevant info, end by logging data
    global settings
    global varcurrent
    global lock
    global comppin
    global eventstarts
    global eventends
    
    while 1: #we want this loop to always be running
        #event list
        date=dt.datetime.today()
        event1start=dt.datetime(date.year,date.month,date.day,12)
        event1end=dt.datetime(date.year,date.month,date.day,13)

        eventstarts=[event1start]#comment this line out to do multi-event timeline
        eventends=[event1end]#comment this line out to do multi-event timeline

        # example of multi-event timeline set-up
        #event3start=dt.datetime(date.year,date.month,date.day,12) 
        #event3end=dt.datetime(date.year,date.month,date.day,20)
        #event4start=dt.datetime(date.year,date.month,date.day,12) 
        #event4end=dt.datetime(date.year,date.month,date.day,20)
        #event5start=dt.datetime(date.year,date.month,date.day,12) 
        # #event5end=dt.datetime(date.year,date.month,date.day,20)
        #eventstarts=[event1start,event2start,event3start,event4start,event5start]
        #eventends=[event1end,event2end,event3end,event4end,event5end]

        lock.acquire() #acquire write permission for varcurrent
        [tempdata,readdatetime]=get_temp(settings["desiredtemp"]) #uncomment to use ubibot thermometer
        #[tempdata,readdatetime]=DAQacquire()
        if settings["UseXMLevent"]==1:#extract ADR data
            [currentstart,duration]=XMLextraction.extractxmldates(settings["XMLfilepath"])
            currentend=currentstart+duration
            settings["event start"]=currentstart;settings["event end"]=currentend
        else:#use event list from settings
            settings["event start"]=eventstarts;settings["event end"]=eventends

        [currentstart, currentend,eventspan,status]=findcurrentevent(settings["event start"],settings["event end"],readdatetime)
        unopttimeneededtocool=InterpcalcV4.interpolatecooling(settings["Lowtempboundary"],tempdata[1],settings["loadmass"])
        optprecoolingtemp=InterpcalcV4.interpolateheating(settings["Hightempboundary"],eventspan,settings["loadmass"])
        opttimeneededtocool=InterpcalcV4.interpolatecooling(optprecoolingtemp,tempdata[1],settings["loadmass"])
        if settings["precooltype"]==3:#use optimal precooling time
            timeneededtocool=dt.timedelta(seconds=opttimeneededtocool)
        else:#use unoptimal precooling time
            timeneededtocool=dt.timedelta(seconds=unopttimeneededtocool)

        
        # this chunk ensures that pre-cool start time is never after the start of an event
        if currentstart-timeneededtocool<currentstart:
            prestart=currentstart-timeneededtocool#precooling start time ideally
            varcurrent["fallbackstart"]=prestart
        elif currentstart-timeneededtocool>=currentstart and varcurrent["fallbackstart"]!=[]:
            prestart=varcurrent["fallbackstart"]
        else:
            varcurrent["fallbackstart"]=currentstart-dt.timedelta(hours=1)
            prestart=currentstart-dt.timedelta(hours=1)

        #update varcurrent with temp data stuff
        #initial set-up of varcurrent
        if settings["precooltype"]==3:#interp precool for both optimal time and temp
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Precoolstart"]=prestart
            varcurrent["Precooltemp"]=optprecoolingtemp;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status

        elif settings["precooltype"]==2:#interp precool for only time
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Precoolstart"]=prestart
            varcurrent["Precooltemp"]=settings["precoolingtemp"];varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status

        elif settings["precooltype"]==1:#manually set pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Precoolstart"]=currentstart-settings["precoolingtime"]
            varcurrent["Precooltemp"]=settings["precoolingtemp"];varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status
        
        else:#no pre-cool
            varcurrent["Datetime"]=readdatetime;varcurrent["Internal air temp"]=tempdata[1];varcurrent["Precoolstart"]= readdatetime
            varcurrent["Precooltemp"]=0;varcurrent["event start"]=currentstart;varcurrent["event end"]=currentend
            varcurrent["event status"]=status
    
        lock.release()#release write permission for varcurrent
       
        #log varcurrent, sleep a certain amount, then repeat loop
        Logthis(varcurrent)
        time.sleep(settings["samplerate"]) # delays iteration of sampling loop to limit sampling rate
        waitforfill.set() #release waitforfill, this ensures that this loop starts before all others and runs at least once every time the program starts
    
def control_loop():
    #take information from logging loop and ADRextraction and figure out what to do with the compressor
    global settings
    global varcurrent
    global waitforfill
    global comppin

    l=waitforfill.wait()#don't start running till logging loop completes an iteration
    
    while 1:#we want this loop to always be running
        if settings["operationmode"]==0:#set the compressor status directly from value in settings
            varcurrent["deadband status"]='N/A'
            if settings["overridecompstatus"]==0:#compressor off
                comppin.off()#turn off control relay
                varcurrent["thermpin"]=0#turn off OEM thermostat
                varcurrent["Compressor status"]=0
            else:#compressor on
                comppin.on()
                varcurrent["thermpin"]=0
                varcurrent["Compressor status"]=1

        elif settings["operationmode"]==1:#use OEM thermostatic control/ OEM digital control
            varcurrent["deadband status"]='N/A'
            comppin.off()#turn off control relay
            varcurrent["thermpin"]=1#turn on OEM control

        elif settings["operationmode"]==2:#use digital control
            varcurrent["thermpin"]=0#turn off OEM control

            if settings["enableADR"]==0:#normal deadband for adr not enabled
                if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                    comppin.off()#control relay off, no need to cool
                    varcurrent["deadband status"]='inbounds'
                elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                    varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                    comppin.off()#control relay off, need to let refrigerator warm up
                    varcurrent["deadband status"]='below bounds'
                else:
                    while varcurrent["Internal air temp"]>=settings["desiredtemp"]-settings["dbandoffset"]:#cool down until we reach the temp we want-a bit of offset for optional overcooling
                        varcurrent["Compressor status"]=1
                        comppin.on()#turn compressor on until air temp is slightly below desired temp
                        varcurrent["deadband status"]='cooling down'
                        time.sleep(settings["samplerate"])
                        
            else:# deadbands for adr enabled
                if varcurrent["event status"]=="during":#keep temp just slightly below high temp for duration of event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                        varcurrent["deadband status"]='inbounds'
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                        varcurrent["deadband status"]='below bounds'
                    else:
                        while varcurrent["Internal air temp"]>=settings["Hightempboundary"]-settings["dbandoffset"]:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below high boundary
                            comppin.on()
                            varcurrent["deadband status"]='cooling down'
                            time.sleep(settings["samplerate"])

                elif varcurrent['Datetime']>varcurrent['Precoolstart'] and varcurrent['event status']=='pre':
                    if varcurrent["Internal air temp"]<varcurrent["Precooltemp"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                        varcurrent["deadband status"]='below bounds'
                    else:
                        while varcurrent["Internal air temp"]>=varcurrent["Precooltemp"]-settings["dbandoffset"] and varcurrent['event status']=='pre':
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()
                            varcurrent["deadband status"]='precooling active'
                            time.sleep(settings["samplerate"])

                elif varcurrent["event status"]=='pre'or varcurrent["event status"]=='post':#normal deadband for pre or post event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()#control relay off, no need to cool
                        varcurrent["deadband status"]='inbounds'             
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()#control relay off, need to let refrigerator warm up
                        varcurrent["deadband status"]='below bounds'
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-settings["dbandoffset"]:
                            varcurrent["Compressor status"]=1#cool down until we reach the temp we want-a bit of offset for optional overcooling
                            comppin.on()
                            varcurrent["deadband status"]='cooling down'
                            time.sleep(settings["samplerate"])

                
                '''
                else:# prior to pre-cooling, normal deadband
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                        varcurrent["deadband status"]='inbounds'
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()    
                        varcurrent["deadband status"]='below bounds'                
                    else:
                        while varcurrent["Internal air temp"]>=settings["desiredtemp"]-settings["dbandoffset"]:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on() 
                            varcurrent["deadband status"]='cooling down'
                            time.sleep(settings["samplerate"])
                            '''

        else:# hybrid operation, use thermostat before event, do slight pre-cooling, keep slightly below during event, then return to thermostat after event
            if settings["enableADR"]==0:
                comppin.off()
                varcurrent["thermpin"]=1
                varcurrent["Compressor status"]=2
                varcurrent["deadband status"]='N/A'
            ## deadbands for adr enabled
            else:
                if varcurrent["event status"]=="during":#keep temp just slightly below high temp for duration of event
                    if varcurrent["Internal air temp"]<=settings["Hightempboundary"] and varcurrent["Internal air temp"]>=settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is within bounds, so compressor is off
                        comppin.off()
                        varcurrent["deadband status"]='inbounds'
                    elif varcurrent["Internal air temp"]<settings["Lowtempboundary"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                        varcurrent["deadband status"]='below bounds'
                    else:
                        while varcurrent["Internal air temp"]>=settings["Hightempboundary"]-settings["dbandoffset"]:
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below high boundary
                            comppin.on()
                            varcurrent["deadband status"]='cooling down'
                            time.sleep(settings["samplerate"])

                elif varcurrent["event status"]=='pre'or varcurrent["event status"]=='post':#return to OEM control
                    comppin.off()
                    varcurrent["thermpin"]=1
                    varcurrent["Compressor status"]=2
                    varcurrent["deadband status"]='N/A'

                elif varcurrent['Datetime']>varcurrent['Precoolstart'] and varcurrent['event status']=='pre':
                    if varcurrent["Internal air temp"]<varcurrent["precoolingtemp"]:
                        varcurrent["Compressor status"]=0 #temp is below bounds, let it heat till back within bounds
                        comppin.off()
                        varcurrent["deadband status"]='below bounds'
                    else:
                        while varcurrent["Internal air temp"]>=varcurrent["precoolingtemp"]-settings["dbandoffset"] and varcurrent['event status']=='pre':
                            varcurrent["Compressor status"]=1#turn compressor on until air temp is slightly below desired temp
                            comppin.on()
                            varcurrent["deadband status"]='precooling active'
                            time.sleep(settings["samplerate"])

                else:# prior to pre-cooling, back to using thermostat
                    comppin.off()
                    varcurrent["thermpin"]=1
                    varcurrent["Compressor status"]=2
                    varcurrent["deadband status"]='N/A'
        time.sleep(settings["samplerate"])                       

def output_loop():
    #display various stats in terminal to check status
    global settings
    global varcurrent
    global waitforfill

    while 1:#always run
        l=waitforfill.wait()#don't start running till logging loop completes an iteration
        print('read time:', varcurrent["Datetime"], 'compressor:',varcurrent["Compressor status"], 'deadbandstatus:',varcurrent["deadband status"], 'air temp:',varcurrent["Internal air temp"], '\n')
        print('event status:',varcurrent["event status"],"precool start:",varcurrent["Precoolstart"],'precooltemp:',varcurrent["Precooltemp"], 'event start:',varcurrent["event start"],'event end:',varcurrent["event end"], '\n')
        time.sleep(settings["samplerate"])
    

def signal_loop():
    #regularly update a pin on the RPi to signal connection between the two computers is good.
    global sigpin
    global settings
    global varcurrent
    i=0
    while 1:
        print(varcurrent["thermpin"])
        if varcurrent["thermpin"]==1:
            sigpin.on()#set sigpin to be constant to intentionally trigger failsafe and put OEM control in charge
        else:
            #switch signal pin state at regular frequency, ensuring it's never constant for too long
            while varcurrent["thermpin"]!=1:
                if i%2==0:
                    sigpin.off()
                else:
                    sigpin.on()
                i=i+1
                time.sleep(settings["samplerate"])
        time.sleep(settings["samplerate"])

## creating threads
loggingloop=threading.Thread(target=logging_loop,args=[])
controlloop=threading.Thread(target=control_loop,args=[])
outputloop=threading.Thread(target=output_loop,args=[])
signalloop=threading.Thread(target=signal_loop,args=[])

## starts threads
loggingloop.start()
controlloop.start()
outputloop.start()
signalloop.start()

print('start')#just letting user know program has started
