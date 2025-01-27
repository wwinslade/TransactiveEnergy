# app/services/__init__.py
# Created by Will Winslade on 1/24/2025

class Device:
  """
  Simple interface for all devices that we aim to control
  """

  def __init__(self, name):
    self.name = name
    self.type = "Unspecified"
    self.ipv4 = None
    self.adr = False
    self.userSpecifiedOffTimes = []
    

    self._state = None
    self._energyConsumption = []

  def on(self):
    raise NotImplementedError
  
  def off(self):
    raise NotImplementedError
  
  def status(self):
    raise NotImplementedError
  
  def enable_adr(self):
    raise NotImplementedError
  
  def disable_adr(self):
    raise NotImplementedError
  
  def set_ipv4(self, ipv4):
    self.ipv4 = ipv4

  def get_ipv4(self):
    return self.ipv4
  
class KasaSwitch(Device):
  """
  Represents a Kasa smart switch
  """
  
  def __init__(self, name, ipv4=None, state=None, adr=False, userSpecifiedOffTimes=[]):
    super().__init__(name)
    self.type = "KasaSwitch"

class Fridge(Device):
  """
  Represents the similated AC (fridge)
  """
  
class DeviceManager:
  """
  Manages multiple devices
  """
  
  def __init__(self):
    self.devices = {}
  
  def add_device(self, name, device):
    self.devices[name] = device
  
  def remove_device(self, name):
    if name in self.devices:
      del self.devices[name]
  
  def get_device(self, name):
    return self.devices.get(name)