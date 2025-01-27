# device.py
# Created by William Winslade on 27 Jan 2025

from abc import ABC, abstractmethod

class SyncDevice(ABC):

  def __init__(self, name):
    self.name = name
    self.type = "Unspecified"
    self.ipv4 = None
    self.userSpecifiedOffTimes = []
    
    self._adr = False
    self._state = None
    self._energyConsumption = []

  @abstractmethod
  def on(self):
    """Turn the device on"""
    pass

  @abstractmethod
  def off(self):
    """Turn off the device"""
    pass

  def get_status(self):
    """Fetch device on/off status"""
    return self._state
  
  @abstractmethod
  def enable_adr(self):
    """Enable ADR on device"""
    pass

  @abstractmethod
  def disable_adr(self):
    """Disable ADR on device"""
    pass

  def set_ipv4(self, ipv4):
    """Set the IPv4 address of a device. Must be in dotted decimal notation."""    
    self.ipv4 = ipv4
    print(f"LOG: Device {self.name} IPv4 updated to {self.ipv4}")

  def get_ipv4(self):
    return self.ipv4
  
  def set_user_offtimes(self, offtimes):
    """Set the times a user wants the device off. Should be a list of intervals in military times"""
    self.userSpecifiedOffTimes = offtimes

  def get_user_offtimes(self):
    """Fetch all specified user off times. Returns list of intervals"""
    return self.userSpecifiedOffTimes
  
class AsyncDevice(ABC):
  def __init__(self, name):
    self.name = name
    self.type = "Unspecified"
    
    
    self.userSpecifiedOffTimes = []
    
    self._ipv4 = None
    self._adr = False
    self._state = None
    self._energyConsumption = []
  
  def get_status(self):
    """Fetch the status of a device"""
    return self._state

  @abstractmethod
  async def on():
    """Turn the asynchronous device on"""
    pass
  
  @abstractmethod
  async def off():
    """Turn the asynchronous device off"""
    pass


  