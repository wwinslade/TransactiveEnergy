import logging
import sys
import random
import matplotlib
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
import matplotlib.pyplot as plt
import threading
import time
import pandas as pd
     
a={"b":1,"c":2}
def input_loop():
    eval(input("to assign values, use str(exec(assignment)): "))
    #eval(str(exec("a['b']=4")))
    print(a)
    #placeholder so I stop getting an indent error on daq loop definition




class Example(threading.Thread):
    def __init__(self):

        # This class inherits from the threading class
        # so we need to initialize it.
        threading.Thread.__init__(self)
        print('Hello from init!')

        # This starts the second thread running.
        self.start()
        while True:
            time.sleep(0.5)

            # print a message from the main thread
            self.main_thread_print()

    def main_thread_print(self):
        print('Hello from the main thread')

    def run(self):
        """
        This method implements the second thread
        """
        while True:
            time.sleep(1)
            print('hello from the second thread')

# instantiate Example
Example()

print("end")