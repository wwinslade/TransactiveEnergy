from ast import Continue
from datetime import datetime
from datetime import timedelta
from email.errors import FirstHeaderLineIsContinuationDefect
from databases import AppData, FridgeData

import time
import requests
import json
import csv
import asyncio
from kasa import SmartPlug
from PricingAPI import PricingAPIHelper 
from ApplianceClass import Appliance, Fridge
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline, BSpline
from numpy.lib.shape_base import apply_over_axes
import RPi.GPIO as GPIO

# Fundtion to plot time v price of energy costs 
def plot_price():
  pricing = PricingAPIHelper()
  # Data to be plotted
  x = pricing.timeArray
  y = pricing.priceArray

  # Formatting and Graphing
  fig,axes=plt.subplots(1,1)
  axes.plot(x, y, color="green")
  axes.xaxis.set_major_locator(MaxNLocator(50)) 
  plt.xticks(fontsize=10, rotation = '55')
  axes.set_title("Today's Estimated Hourly Electricity Price", fontsize=24)
  axes.set_xlabel("Time", fontsize=18)
  axes.set_ylabel("Price (Cents)", fontsize=18)
  fig.set_size_inches(12, 9, forward=True)
  
  # Path of Plot
  plt.savefig("/home/pi/Documents/ProjectFiles/webapp/ALPSCode_2022/static/img/myplot.png", dpi = 200)

  # Save data to csv file
  with open('data.csv', 'a', newline='') as f:  
    writeFile = csv.writer(f)
    writeFile.writerow(['Time','Price'])

    for i in range(len(x)):
      writeFile.writerow([x[i], y[i]])


# Retrieves temp through Ubibot API
# API Documentation https://www.ubibot.com/platform-api/1232/quick-start/
def get_temp():
  account_key = "54183910b6a04fd59648e022d58a1229"
  channel = "42895"
  API_link = str("https://api.ubibot.com/channels/%s?account_key=%s"%(channel, account_key))
  API_response = requests.get(API_link).json()

  Json = json.loads(API_response["channel"]["last_values"])
  temperature = Json["field1"]["value"]
  temperature = round(temperature * 9/5 + 32, 0)

  return temperature 

# IP for kasa smart switches found by typing "kasa discover" in command line
switch1_IP = "192.168.0.102"
switch2_IP = "192.168.0.103"
switch3_IP = "192.168.0.104"
switch4_IP = "192.168.0.105"
switch5_IP = "192.168.0.106"
switch6_IP = "192.168.0.107"
switch7_IP = "192.168.0.108"
switch8_IP = "192.168.0.109"

if __name__ == '__main__':
  print("\nAPIHelper #1\n")
  plot_price()
  print("\ngetAppliances #1\n")
  appliances = AppData.getAppliances("sewellnoah@gmail.com")
  # Initialize appliances
  # Format: Appliance(applianceName, currState, adrEnabled, IP_address, priceThreshold, userOffTime, userOnTime, prevState)
  print("\nLight #1")
  light1 = Appliance("lightbulb1", "on", True, switch5_IP, ["4:40PM", "2:14PM"], ["12:28PM", "1:13PM"], "off")
  print("\nLight #2")
  light2 = Appliance("lightbulb2", "on", True, switch6_IP, ["2:13PM", "2:14PM"], ["1:01PM", "1:02PM"], "off")
  print()
  # Format: Fridge(priceThreshold, priceThreshold, currState, adrEnabled, desiredTemp, highBoundary, lowBoundary, deadBand, minsBefore)
  fridge = FridgeData.getFridge("sewellnoah@gmail.com")
  fridge = Fridge("Fridge1", "default", 1, 44, 47, 42, "off", 30)

  # Append all appliances
  appliances.append(light1)
  appliances.append(light2)
  print("\ngetAppliances #2\n")
  appliances = AppData.getAppliances("sewellnoah@gmail.com")

  # Appliance data
  print("\nOutputting Grabbed Data\n")
  for app in appliances:
    print("Appliance          : " + str(app.applianceName))
    print("Price Threshold    : " + str(app.priceThreshold) + " cents")
    print("ADR Enabled        : " + str(app.adrEnabled))
    if(app.userOffTime):
      print("User Set Off Times : " + str(app.userOffTime[0])  + " - " + str(app.userOffTime[1]))
    if(app.userOnTime):
      print("User Set On Times  : " + str(app.userOnTime[0])  + " - " + str(app.userOnTime[1]))
    if(app.adrOffTimes):
      print("ADR Off Times      : " + str(app.adrOffTimes))
    print()
  
  # Fridge Data
  print("Appliance            : " + str(fridge.applianceName))
  print("ADR Enabled          : " + str(fridge.adrEnabled))
  if(fridge.adrOffTimes):
    print("ADR Off Times      : " + str(fridge.adrOffTimes))

  currentTemp = get_temp()

  print("\nEntering the while loop\n")
  #################### Encase everything after in while loop #########################
  try:
    while(1):
      appliances = AppData.getAppliances("sewellnoah@gmail.com")
      fridge = FridgeData.getFridge("sewellnoah@gmail.com")
      #bools for database updates
      deadBandBool = False #updateFridgeDeadBand(app_name, deadBand):
      currStateBool = False #updateFridgeState(app_name, state):

      #populate objects :: TODO
      
      #time.sleep(1)

      # Get the current time in military time
      now = datetime.now()
      currentTime = now.strftime("%X")
      total_s = int(now.timestamp())

      # Get temp every 30 s 
      try:
        if(total_s % 30 == 0):
          currentTemp = get_temp()
      except: 
        print("Issue with getting temperature")
      
      print("\n\nCurrent Time: " + currentTime)


      ########################################## Fridge Logic ################################################
      
      # Get pricing data only at Midnight (with some offset)
      if(currentTime > "23:58:00" and currentTime < "23:59:00"):
        plot_price()
        fridge.ADR()

      # Fridge ADR logic incased within this IF statement
      if(fridge.adrEnabled == True):
        offset = 10 # in minutes
        for offTime in fridge.adrOffTimes:
          
          # Create upper-bound and lower-bound for off-times using some offset
          upperBound = datetime.strptime(offTime, "%H:%M:%S") + timedelta(minutes=offset)
          lowerBound = datetime.strptime(offTime, "%H:%M:%S") - timedelta(minutes=offset)
          upperBound = upperBound.time().strftime("%X")
          lowerBound = lowerBound.time().strftime("%X")

          # Bounds to start pre-cooling prior to ADR event 
          #print(type(fridge.minsBefore))
          precooling = datetime.strptime(lowerBound, "%H:%M:%S") - timedelta(minutes=fridge.minsBefore)
          #precooling = datetime.strptime(lowerBound, "%H:%M:%S") - fridge.minsBefore
          precooling = precooling.time().strftime("%X")
          
          # Set the state to pre-cool the fridge and turn off any previous debanding state
          if(currentTime >= precooling and currentTime < lowerBound):
            fridge.deadBand = "off"
            fridge.currState = "Pre-Cooling"
            fridge.fridge_control("on")
            break

          # If current time falls within ADR off-times and temperature bounds, turn off fridge
          elif(currentTime >= lowerBound and currentTime <= upperBound):
            
            # Keep fridge on unless high boundary is exceeded
            if(currentTemp >= fridge.lowBoundary and currentTemp <= fridge.highBoundary and fridge.deadBand == "off"):
              fridge.currState = "off"
              fridge.fridge_control("off")
            elif(currentTemp <= fridge.lowBoundary):
              fridge.currState = "off"
              fridge.fridge_control("off")

            # Compressor turns on & deadBand control kicks in to keep fridge from rubberbanding
            elif(currentTemp >= fridge.highBoundary or fridge.deadBand == "on"): 
              fridge.currState = "on"
              fridge.fridge_control("on")
              fridge.deadBand = "on"
              if(currentTemp <= fridge.desiredTemp):
                fridge.deadBand = "off"
            break

          # Fridge default behavoir similar to the adr logic without precooling
          else:
            fridge.currState = "default"
          #update database?

      if(fridge.adrEnabled == False or fridge.currState == "default"):
        # Keep fridge off unless it reaches highboundary
        if(currentTemp >= fridge.lowBoundary and currentTemp <= fridge.highBoundary and fridge.deadBand == "off"):
          fridge.fridge_control("off")
        elif(currentTemp <= fridge.lowBoundary):
          fridge.fridge_control("off")

        # Turn on fridge if it reaches high boundary until it reaches desired temperature
        elif(currentTemp >= fridge.highBoundary or fridge.deadBand == "on"):
          fridge.fridge_control("on")
          fridge.deadBand = "on"
          if(currentTemp <= fridge.desiredTemp):
            fridge.deadBand = "off"  

      print("Fridge is " + fridge.currState)
      print("Fridge deadBand is " + fridge.deadBand)
      print("Current Temperature: %d"%currentTemp)
      
      ########################################## Appliance Logic ################################################

      for app in appliances:

        # Get pricing data only at Midnight (with some offset)
        if(currentTime > "23:58:00" and currentTime < "23:59:00"):
          plot_price()
          app.ADR()

        # Apply ADR off times only if ADR is enabled for appliance
        if(app.adrEnabled == True):
          offset = 5 # in minutes

          for offTime in app.adrOffTimes:
            
            # Create upper-bound and lower-bound for off-times using some offset
            upperBound = datetime.strptime(offTime, "%H:%M:%S") + timedelta(minutes=offset)
            lowerBound = datetime.strptime(offTime, "%H:%M:%S") - timedelta(minutes=offset)
            upperBound = upperBound.time().strftime("%X")
            lowerBound = lowerBound.time().strftime("%X")
            
            # If current time falls within ADR off-times, turn off appliance and break loop
            if(currentTime >= lowerBound and currentTime < upperBound):
              app.ADR = "on"
              app.done = False
              break
            elif(currentTime == upperBound):
              app.ADR = "off"
              app.done = True
            else:
              app.ADR = "off"
        
        # On within user-on-times
        if(app.userOnTime and currentTime >= app.userOnTime[0] and currentTime < app.userOnTime[1]):
          app.currState = "on"
        # Off within user-off-times
        elif(app.userOffTime and currentTime >= app.userOffTime[0] and currentTime < app.userOffTime[1]):
          app.currState = "off"
        # Off during ADR events
        elif(app.ADR == "on"):
          app.currState = "off"
        else:
          # Update state to prev state at the end of ADR event or user on and off times
          if(app.done == True or (app.userOnTime and currentTime == app.userOnTime[1]) or (app.userOffTime and currentTime == app.userOffTime[1])):
            app.currState = app.prevState
          app.prevState = app.currState
        
        # Update switch based on appliance's current state
        print(app.applianceName + " is " + app.currState)
        print(type(app.currState))
        asyncio.run(app.switch(app.currState))


  except:
    for app in appliances:
      asyncio.run(app.switch("off"))

    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.output(4, GPIO.HIGH)   