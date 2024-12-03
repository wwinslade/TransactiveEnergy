import argparse
import logging

from rpi_rf import RFDevice

def send_code(code):
    gpio =  23
    pulselength = 185
    protocol = 1
    length = 24
    repeat = 10
    
    rfdevice = RFDevice(gpio)
    rfdevice.enable_tx()
    rfdevice.tx_repeat = repeat


   
    rfdevice.tx_code(code,protocol,pulselength,length)
    rfdevice.cleanup()

send_code(349500)
