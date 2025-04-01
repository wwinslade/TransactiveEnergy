from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from datetime import datetime

from .models import Device, KasaSwitch, Fridge
from apps.devices.services.kasa import KasaSwitchAPI
from apps.devices.services.fridge import FridgeAPI

import asyncio

executors = {
  'default': ThreadPoolExecutor(4),
}

scheduler = BackgroundScheduler(executors=executors)

def device_turn_on(uuid, type):
  if type == 'kasa_switch':
    switch = KasaSwitch.objects.get(device__uuid=uuid)
    switch_api = KasaSwitchAPI(switch.ip_address)
    asyncio.run(switch_api.off())

    switch.device.status = True
    switch.device.save()
  elif type == 'fridge':
    fridge = Fridge.objects.get(device__uuid=uuid)
    fridge_api = FridgeAPI()

    fridge_api.on()
    
    fridge.device.status = True
    fridge.device.save()
  else:
    print('Device on task failed: Unknown device type')

def device_turn_off(uuid, type):
  if type == 'kasa_switch':
    switch = KasaSwitch.objects.get(device__uuid=uuid)
    switch_api = KasaSwitchAPI(switch.ip_address)
    asyncio.run(switch_api.off())

    switch.device.status = True
    switch.device.save()
  elif type == 'fridge':
    fridge = Fridge.objects.get(device__uuid=uuid)
    fridge_api = FridgeAPI()

    fridge_api.on()
    
    fridge.device.status = True
    fridge.device.save()
  else:
    print('Device off task failed: Unknown device type')

def start():
  if not scheduler.running:
    scheduler.start()

    devices = Device.objects.filter(use_user_window=True)
    for d in devices:
      data = {'device_uuid': d.uuid, 'device_type': d.type, 'on_window_begin': d.on_window_begin, 'on_window_end': d.on_window_end}
      scheduler.add_job(
        device_turn_on,
        'cron',
        hour = d.on_window_begin.hour,
        minute = d.on_window_begin.minute,
        args = [d.uuid, d.type],
        id = f'device_{d.uuid}_{d.type}_ON'
      )

      scheduler.add_job(
        device_turn_off,
        'cron',
        hour = d.on_window_end.hour,
        minute = d.on_window_end.minute,
        args = [d.uuid, d.type],
        id = f'device_{d.uuid}_{d.type}_ON'
      )

    print('Scheduler started')


