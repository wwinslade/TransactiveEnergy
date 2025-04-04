# kasa_switch.py
# Created by William Winslade on 27 Jan 2025

from .device import AsyncDevice
from kasa import SmartPlug
import asyncio

# Kasa Library documentation is here, but the version referenced by the previous project 
# appears to be deprecated. Need to investigate further at some point

'''
This file defines the KasaSwitch class, a child class of the AsyncDevice interface
as defined in services/device.py

We're using the kasa-python library to interact with the switches, which requires us
to use asynchronous IO. 
'''

class KasaSwitchAPI(AsyncDevice):
  def __init__(self, ipv4):
    self.ipv4 = ipv4

  async def on(self):
    self._switch = SmartPlug(self.ipv4)
    await self._switch.turn_on()
    
    self._status = True
    print(f"DEBUG: Switch @ {self.ipv4} successfully turned on")

  async def off(self):
    self._switch = SmartPlug(self.ipv4)
    await self._switch.turn_off()

    self._status = False
    print(f"DEBUG: Switch @ {self.ipv4} successfully turned off")

  