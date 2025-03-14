from apps.devices.models import Device, KasaSwitch, Fridge, EnergyConsumption

from celery import shared_task

from apps.devices.services.kasa import KasaSwitchAPI

import asyncio

@shared_task
def CeleryKasaSwitchOn(uuid):
  switch = KasaSwitch.objects.get(device__uuid=uuid)
  switch_api = KasaSwitchAPI(switch.ip_address)

  asyncio.run(switch_api.on())

  switch.device.status = True
  switch.device.save()