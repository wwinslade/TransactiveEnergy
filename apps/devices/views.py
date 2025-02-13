from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.devices.services.kasa import KasaSwitchAPI
from apps.devices.services.fridge import FridgeAPI

from .models import Device, KasaSwitch, Fridge

import asyncio

# Create your views here.
@login_required()
def KasaSwitchOn(request, uuid):
  switch = KasaSwitch.objects.get(uuid=uuid)
  switch_api = KasaSwitchAPI(switch.ipv4)
  
  # Note: This is a blocking call :(
  asyncio.run(switch_api.on())

  switch.status = True
  switch.save()

  return HttpResponse("Switch turned on and status updated.")

@login_required()
def KasaSwitchOff(request, uuid):
  switch = KasaSwitch.objects.get(uuid=uuid)
  switch_api = KasaSwitchAPI(switch.ipv4)
  
  # Note: This is a blocking call :(
  asyncio.run(switch_api.off())

  switch.status = False
  switch.save()

  return HttpResponse("Switch turned off and status updated.")


