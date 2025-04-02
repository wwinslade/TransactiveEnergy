from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from datetime import datetime

from .models import Device, KasaSwitch, Fridge
from apps.devices.services.kasa import KasaSwitchAPI
from apps.devices.services.fridge import FridgeAPI

import asyncio

import os
import threading

import atexit

executors = {
  'default': ThreadPoolExecutor(4),
}

scheduler = BackgroundScheduler(executors=executors)

def device_turn_on(uuid, type):
  if type == 'kasa_switch':
    switch = KasaSwitch.objects.get(device__uuid=uuid)
    switch_api = KasaSwitchAPI(switch.ip_address)
    asyncio.run(switch_api.on())

    switch.device.status = True
    switch.device.save(update_fields=['status'])
  elif type == 'fridge':
    fridge = Fridge.objects.get(device__uuid=uuid)
    fridge_api = FridgeAPI()

    fridge_api.on()
    
    fridge.device.status = True
    fridge.device.save(update_fields=['status'])
  else:
    print('Device on task failed: Unknown device type')
  
  print(f'DEBUG: ScheduledEventRan: Turned device {uuid} ON at {datetime.now()}')

def device_turn_off(uuid, type):
  if type == 'kasa_switch':
    switch = KasaSwitch.objects.get(device__uuid=uuid)
    switch_api = KasaSwitchAPI(switch.ip_address)
    asyncio.run(switch_api.off())

    switch.device.status = True
    switch.device.save(update_fields=['status'])
  elif type == 'fridge':
    fridge = Fridge.objects.get(device__uuid=uuid)
    fridge_api = FridgeAPI()

    fridge_api.off()
    
    fridge.device.status = True
    fridge.device.save(update_fields=['status'])
  else:
    print('Device off task failed: Unknown device type')

  print(f'DEBUG: ScheduledEventRan: Turned device {uuid} OFF at {datetime.now()}')

def reschedule_device(device):
  on_job_id = f'device_{device.uuid}_{device.type}_ON_{device.on_window_begin.hour}_{device.on_window_begin.minute}'
  off_job_id = f'device_{device.uuid}_{device.type}_OFF_{device.on_window_begin.hour}_{device.on_window_begin.minute}'

  if scheduler.get_job(on_job_id):
    scheduler.remove_job(on_job_id)
    print(f'Removed job: {on_job_id}')

  if scheduler.get_job(off_job_id):
    scheduler.remove_job(off_job_id)
    print(f'Removed job: {off_job_id}')

  print(f'Added job: device_{device.uuid}_{device.type}_ON_{device.on_window_begin.hour}_{device.on_window_begin.minute}')
  scheduler.add_job(
    device_turn_on,
    'cron',
    hour = device.on_window_begin.hour + 4, # account for UTC time
    minute = device.on_window_begin.minute,
    args = [device.uuid, device.type],
    id = f'device_{device.uuid}_{device.type}_ON_{device.on_window_begin.hour}_{device.on_window_begin.minute}'
  )

  print(f'Added job: device_{device.uuid}_{device.type}_OFF_{device.on_window_end.hour}_{device.on_window_end.minute}')
  scheduler.add_job(
    device_turn_off,
    'cron',
    hour = device.on_window_end.hour + 4, # account for UTC time
    minute = device.on_window_end.minute,
    args = [device.uuid, device.type],
    id = f'device_{device.uuid}_{device.type}_OFF_{device.on_window_end.hour}_{device.on_window_end.minute}'
  )

@receiver(post_save, sender=Device)  
def update_jobs_on_save(sender, instance, update_fields=None, **kwargs):
  # Only run the rescheduling function on the device if it is freshly created, or if relevant fields were updated
  # By default, when instance.save() is called, Django assumes all fields are updated, and update_fields == None
  if update_fields is None or any(field in update_fields for field in ['use_user_window', 'on_window_begin', 'on_window_end']):
    print(f'DEBUG: Updating scheduler jobs for device {instance.name}')
    
    if instance.use_user_window == False:
      on_job_id = f'device_{instance.uuid}_{instance.type}_ON_{instance.on_window_begin.hour}_{instance.on_window_begin.minute}'
      off_job_id = f'device_{instance.uuid}_{instance.type}_OFF_{instance.on_window_end.hour}_{instance.on_window_end.minute}'
      scheduler.remove_job(on_job_id)
      print(f'Removed job: {on_job_id}')
      scheduler.remove_job(off_job_id)
      print(f'Removed job: {off_job_id}')
      
      return

    reschedule_device(instance)
    print(f"DEBUG: Device {instance.name} scheduled on/off tasks updated")

@receiver(post_delete, sender=Device)
def remove_jobs_on_delete(sender, instance, **kwargs):
  on_job_id = f'device_{instance.uuid}_{instance.type}_ON_{instance.on_window_begin.hour}_{instance.on_window_begin.minute}'
  off_job_id = f'device_{instance.uuid}_{instance.type}_OFF_{instance.on_window_begin.hour}_{instance.on_window_begin.minute}'

  if scheduler.get_job(on_job_id):
    scheduler.remove_job(on_job_id)
    print(f'Removed job: {on_job_id}')
  
  if scheduler.get_job(off_job_id):
    scheduler.remove_job(off_job_id)
    print(f'Removed job: {off_job_id}')
  
  print(f'DEBUG: ON/OFF jobs for device {instance.name} removed from scheduler')

def start():
  if not scheduler.running:
    print(f"Scheduler started in PID: {os.getpid()}, Thread: {threading.current_thread().name}")

    scheduler.start()
    scheduler.remove_all_jobs()

    devices = Device.objects.filter(use_user_window=True)
    for d in devices:
      print(f'Added job: device_{d.uuid}_{d.type}_ON_{d.on_window_begin.hour}_{d.on_window_begin.minute}')
      scheduler.add_job(
        device_turn_on,
        'cron',
        hour = d.on_window_begin.hour + 4, # account for UTC time
        minute = d.on_window_begin.minute,
        args = [d.uuid, d.type],
        id = f'device_{d.uuid}_{d.type}_ON_{d.on_window_begin.hour}_{d.on_window_begin.minute}'
      )

      print(f'Added job: device_{d.uuid}_{d.type}_OFF_{d.on_window_end.hour}_{d.on_window_end.minute}')
      scheduler.add_job(
        device_turn_off,
        'cron',
        hour = d.on_window_end.hour + 4, # account for UTC time
        minute = d.on_window_end.minute,
        args = [d.uuid, d.type],
        id = f'device_{d.uuid}_{d.type}_OFF_{d.on_window_end.hour}_{d.on_window_begin.minute}'
      )

    atexit.register(stop_scheduler)
    print('Device ON/OFF event scheduler started')

def stop_scheduler():
  if scheduler.running:
    print('Device ON/OFF event scheduler killed')
    scheduler.shutdown()
