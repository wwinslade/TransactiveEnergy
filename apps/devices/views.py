from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.services.kasa import KasaSwitchAPI
from apps.devices.services.fridge import FridgeAPI

from .models import Device, KasaSwitch, Fridge, EnergyConsumption

import asyncio
import requests
from datetime import datetime
from django.utils import timezone

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

@login_required()
def QueryIotaWatt(request):
  '''
  In the future, this should be moved to a celery async task

  Queries IotaWatt device for energy consumption data at a given time interval and sample interval.
  Query params are passed in the URL:
  - begin: The start time of the query (default: d-1d)
  - end: The end time of the query (default: d)
  - interval: The sample interval (default: 10m)
  Time format follows ISO relative to current time. More information on crafting a query:

  For more time format information: https://docs.iotawatt.com/en/master/query.html#relative-time
  '''

  range_begin = request.GET.get('begin', 'd-1d')
  range_end = request.GET.get('end', 'd')
  sample_interval = request.GET.get('interval', '10m')

  url = f'http://192.168.0.111/query?select=[time.iso,input_0,Fridge,Solar,Recepticles]&begin={range_begin}&end={range_end}&group={sample_interval}&format=json&header=yes'
  response = requests.get(url)
  if response.status_code != 200:
    print(f'Error fetching data from IotaWatt: {response.status_code} @ {url}')
    return None

  times = response.json().get('range', [])
  times = [datetime.fromtimestamp(time) for time in times]
  
  labels = response.json().get('labels', [])
  data = response.json().get('data', [])

  print(f'IotaWatt Data fetched for {sample_interval} interval from {times[0]} to {times[-1]}')

  # Save the data to the EnergyConsumption model
  for d in data:
    timestamp = datetime.fromisoformat(d[0])
    timestamp = timezone.make_aware(timestamp)
    input_0 = d[1]
    fridge = d[2]
    recepticles = d[4]

    # Create a new EnergyConsumption object
    fridge_energy_consumption = EnergyConsumption(
      label = 'fridge',
      timestamp = timestamp,
      energy_consumed = fridge
    )

    recepticle_energy_consumption = EnergyConsumption(
      label = 'recepticles',
      timestamp=timestamp,
      energy_consumed=recepticles
    )

    # Save the object to the database
    fridge_energy_consumption.save()
    recepticle_energy_consumption.save()

  print(f'Energy consumption data saved to DB for {sample_interval} interval from {times[0]} to {times[-1]}')

  return HttpResponse('IotaWatt data fetched and saved successfully.')