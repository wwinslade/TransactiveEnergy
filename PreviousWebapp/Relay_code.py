import RPi.GPIO as GPIO 
from time import sleep 

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

try: 
	while True:
        
		Driver_status = open("Driver Status.txt","r+")
		print ("Driver Status is")
		state = int((Driver_status.readline(1)))
		
		if state==1:
			print ('ON')
			GPIO.output(24, GPIO.LOW)
		    
		if state==0:
			print ('OFF')
			GPIO.output(24, GPIO.HIGH)
			
		sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
	
