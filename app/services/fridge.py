# fridge.py
# Created by William Winslade on 27 Jan 2025

from .device import SyncDevice
import RPi.GPIO as GPIO

'''
This file defines the Fridge class, a child class of the SyncDevice interface
as defined in services/device.py

The fridge for this project is controlled by an external relay board that we interact
with using the Pi's GPIO pins. The RPi.GPIO library is used to that end.
'''

class Fridge(SyncDevice):
  """class Fridge is a child class of the interface SyncDevice"""
  
  def __init__(self, name):
    super().__init__(name)
    self.type = "GPIO Controlled Minifridge"
    
    # Setup the GPIO API
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)

  def __del__(self):
    '''This destructor is called when the fridge object is to be deleted. Will cleanup the RPi GPIO library'''
    
    GPIO.cleanup()
    print(f"DEBUG: Fridge {self.name} is being deleted, cleaning up GPIO")

  def on(self):
    """Turn the fridge on"""
    GPIO.output(4, GPIO.LOW)

    self._state = True
    print(f"DEBUG: Fridge {self.name} was turned on successfully")

  def off(self):
    """Turn the fridge off"""
    GPIO.output(4, GPIO.HIGH)

    self._state = False
    print(f"DEBUG: Fridge {self.name} was turned off successfully")

  def enable_adr(self):
    raise NotImplementedError

  def disable_adr(self):
    raise NotImplementedError 

