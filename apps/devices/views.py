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