from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.services.kasa import KasaSwitchAPI
from apps.devices.services.fridge import FridgeAPI

from .models import Device, KasaSwitch, Fridge, EnergyConsumption

import asyncio
import requests
from datetime import datetime
from django.utils import timezone

from django.http import JsonResponse

import numpy as np
import threading
from datetime import datetime


# Create your views here.
@login_required()
def KasaSwitchOn(request, uuid):
  switch = KasaSwitch.objects.get(device__uuid=uuid)
  switch_api = KasaSwitchAPI(switch.ip_address)
  
  # Note: This is a blocking call :(
  asyncio.run(switch_api.on())

  switch.device.status = True
  switch.device.save()

  return redirect('admin')

@login_required()
def KasaSwitchOff(request, uuid):
  switch = KasaSwitch.objects.get(device__uuid=uuid)
  switch_api = KasaSwitchAPI(switch.ip_address)
  
  # Note: This is a blocking call :(
  asyncio.run(switch_api.off())

  switch.device.status = False
  switch.device.save()

  return redirect('admin')

@login_required()
def FridgeOn(request, uuid):
  fridge = Fridge.objects.get(device__uuid=uuid)
  fridge_api = FridgeAPI()
  
  # Note: This is a blocking call :(
  fridge_api.on()

  fridge.device.status = True
  fridge.device.save()

  return redirect('admin')

@login_required()
def FridgeOff(request, uuid):
  fridge = Fridge.objects.get(device__uuid=uuid)
  fridge_api = FridgeAPI()
  
  # Note: This is a blocking call :(
  fridge_api.off()

  fridge.device.status = False
  fridge.device.save()

  return redirect('admin')

# Battery percentage levels and corresponding total time in minutes
battery_percentages = np.array([100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 
                                45, 40, 35, 30, 25, 20, 15, 10, 5, 0])
total_time_minutes = np.array([0, 1, 23, 36, 47, 55, 64, 74, 82, 91, 99, 
                               107, 114, 120, 126, 132, 138, 155, 171, 181, 193])

# Quadratic model coefficients
d, e, f = np.polyfit(battery_percentages, total_time_minutes[::-1], 2)

def estimate_remaining_time(battery_percentage):
    """Estimate the remaining battery time based on percentage."""
    return max(0, d * battery_percentage**2 + e * battery_percentage + f)

# Battery tracking variables
battery_percentage = 100  # Start at full charge
index = 0  # Index for battery percentage updates
remaining_time = estimate_remaining_time(battery_percentage)
time_intervals = np.diff(total_time_minutes) * 60  # Convert to seconds

def update_battery():
    """Update battery percentage."""
    global battery_percentage, index, remaining_time
    
    if index < len(time_intervals):
        battery_percentage = battery_percentages[index]  # Update battery percentage
        remaining_time = estimate_remaining_time(battery_percentage)  # Update estimated time
        index += 1
        
        # Schedule next update
        threading.Timer(time_intervals[index-1], update_battery).start()
        print(f"Battery updated: {battery_percentage}%, Estimated Time: {remaining_time // 60}h {remaining_time % 60}m")

# Start the battery drain simulation
update_battery()
