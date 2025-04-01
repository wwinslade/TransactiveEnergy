from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from datetime import datetime

from .models import Device

executors = {
  'default': ThreadPoolExecutor(4),
}

scheduler = BackgroundScheduler(executors=executors)

def trigger_device_event(device_uuid, action):
  return

def start():
  if not scheduler.running:
    scheduler.start()

    device_schedules = []

    devices = Device.objects.filter(use_user_window=True)
    for d in devices:
      device_schedules.append({'device_uuid': d.uuid, 'on_window_begin': d.on_window_begin, 'on_window_end': d.on_window_end})



