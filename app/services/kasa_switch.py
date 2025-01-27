from .device import AsyncDevice
from kasa import SmartPlug
import asyncio

# Kasa Library documentation is here, but the version referenced by the previous project 
# appears to be deprecated. Need to investigate further at some point


class KasaSwitch(AsyncDevice):
  def __init__(self, name, ipv4):
    """Init for KasaSwitches"""
    super().__init__(name)
    
    self.type = "Kasa SmartPlug"
    self._ipv4 = ipv4

    # Call the Kasa library
  async def on(self):
    self._switch = SmartPlug(self._ipv4)
    await self._switch.turn_on()
    
    self._status = True
    print(f"DEBUG: Switch {self.name} @ {self._ipv4} successfully turned on")

  async def off(self):
    self._switch = SmartPlug(self._ipv4)
    await self._switch.turn_off()

    self._status = False
    print(f"DEBUG: Switch {self.name} @ {self._ipv4} successfully turned off")

  