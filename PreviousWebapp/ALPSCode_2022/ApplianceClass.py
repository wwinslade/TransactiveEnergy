from threading import currentThread
from sniffio import current_async_library
#from ALPSCode_2022.PricingAPI import PricingAPIHelper 
from PricingAPI import PricingAPIHelper 
from datetime import datetime, timedelta
import RPi.GPIO as GPIO 
from time import sleep 
import asyncio
import numpy as np
from kasa import SmartPlug

'''
Login for Kasa Smart Switches
  User: dwhite69@vols.utk.edu
  Pass: Alps2022!
Login for Ubibot Smart Thermometer
  User: alps2022
  Pass: Alps2022!
'''

# Class for all appliances & smart switches
# Push from main CurrState PrevState
# Pull from Website CurrState ADRenable PriceThreshold PrevState
class Appliance:
    applianceName = ""
    priceThreshold = 0
    userOffTime = []
    userOnTime = []
    adrOffTimes = []
    currState = None
    prevState = None
    adrEnabled = None
    ADR = ""
    done = False

    def __init__(self, applianceName, currState, adrEnabled, IP_address, userOffTime=None, userOnTime=None, prevState=None): #do not change bfore texting me, Noah S.
        pricing = PricingAPIHelper()

        # Initialize member variables
        self.applianceName = applianceName
        self.userOffTime = userOffTime
        self.userOnTime = userOnTime
        self.currState = currState
        self.prevState = prevState
        self.adrEnabled = adrEnabled
        self.IP_address = IP_address

        # Determine user specified off times in military time
        if(self.userOffTime and self.userOffTime[0] != "" and self.userOffTime[1] != ""):
            self.userOffTime[0] = datetime.strptime(self.userOffTime[0], '%I:%M%p').strftime("%X")
            self.userOffTime[1] = datetime.strptime(self.userOffTime[1], '%I:%M%p').strftime("%X")
        

        # Determine user specified on times in military time
        if(self.userOnTime and self.userOnTime[0] != "" and self.userOnTime[1] != ""):
            self.userOnTime[0] = datetime.strptime(self.userOnTime[0], '%I:%M%p').strftime("%X")
            self.userOnTime[1] = datetime.strptime(self.userOnTime[1], '%I:%M%p').strftime("%X")
            
        self.ADR()
        #insert application into the database
        #data.newAppliance(...)

    # Helper function to populate ADR event times    
    def ADR(self):
        pricing = PricingAPIHelper()
        print("\t\tPricingAPIHelper complete")

        # Time and Price arrays
        timeArray = pricing.timeArray
        priceArray = pricing.priceArray

        # Find the 10 higest pricing peaks and append to ADR events
        n = 10
        indices = sorted(range(len(priceArray)), key = lambda sub: priceArray[sub])[-n:]
        avg = np.average(priceArray)
        offTimes = []
        for i in indices:
            if(priceArray[i] > avg):
                offTimes.append(timeArray[i])

        self.adrOffTimes = offTimes

    # Control function for smart switches through ip address
    # Python-kasa documentation https://python-kasa.readthedocs.io/en/latest/smartdevice.html
    async def switch(self, on_off):
        print(type(self.IP_address))
        switch = SmartPlug(self.IP_address)
        # await switch.update()

        if on_off == "true":
            await switch.turn_on()
                
        else:
            await switch.turn_off()

# Fridge class for initilizing and populating adr events
# Push from main CurrState & CurrentTemp
# Pull from website the ADREnable
class Fridge:
    priceThreshold = 0
    adrOffTimes = []
    currState = None
    adrEnabled = None
    desiredTemp = 0
    highBoundary = 0
    lowBoundary = 0
    deadBand = None
    minsBefore = 0
    applianceName = ""

    def __init__(self, applianceName, currState, adrEnabled, desiredTemp, highBoundary, lowBoundary, deadBand, minsBefore):
        pricing = PricingAPIHelper()

        # Initialize member variables
        self.applianceName = applianceName
        self.currState = currState
        self.adrEnabled = adrEnabled
        self.desiredTemp = desiredTemp
        self.highBoundary = highBoundary
        self.lowBoundary = lowBoundary
        self.deadBand = deadBand
        self.minsBefore = minsBefore
            
        self.ADR()

    # ADR helper function to call API & populate events
    def ADR(self):
        pricing = PricingAPIHelper()

        # Time and Price arrays
        timeArray = pricing.timeArray
        priceArray = pricing.priceArray

        # Find the 10 higest pricing peaks and append to ADR events
        n = 10
        indices = sorted(range(len(priceArray)), key = lambda sub: priceArray[sub])[-n:]
        avg = np.average(priceArray)
        offTimes = []
        for i in indices:
            if(priceArray[i] > avg):
                offTimes.append(timeArray[i])

        self.adrOffTimes = offTimes
    
    # Fridge control logic via GPIO ports to relay
    def fridge_control(self, on_off):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT)
        
        if on_off == "on":
            GPIO.output(4, GPIO.LOW)
            
        elif on_off == "off":
            GPIO.output(4, GPIO.HIGH)          

