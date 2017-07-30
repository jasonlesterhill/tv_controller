from threading import Thread
import RPi.GPIO as GPIO
import time
import os
import sys

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
processId = str(os.getpid())
sys.stdout = open('/tmp/tv_switch_' + processId, 'w')

def startDown():
	os.system("python /var/www/html/tv/tv_motion.py 0 wall_switch_down")

def startUp():
	os.system("python /var/www/html/tv/tv_motion.py 1 wall_switch_up")

print "TV Switch Started"
last_state = GPIO.input(17)
lastTime = time.time();
while True:
    input_state = GPIO.input(17)
    if last_state != input_state:
	print "Toggle..." + str(time.time())
	os.system("python /var/www/html/tv/stop.py Toggle_Initial_Stop")
	if (0 != os.system("ping -c 1 192.168.1.13 > /tmp/j_home_log")):
		print "Jason Not Home so Not moving..."
		os.system("python /var/www/html/tv/stop.py Jason_Not_Home")
		last_state = input_state
		continue
	if ((time.time() - lastTime) < 1):
		print "Toggle Too Fast, Stopping. " + str(time.time() - lastTime)
		os.system("python /var/www/html/tv/stop.py Toggle_to_fast")
		last_state = input_state
		lastTime = time.time();
		continue
	if input_state == False:
        	print('Button Pressed TV Up')
    		time.sleep(.1)
		thread = Thread( target=startUp ).start()
        	print('Button Pressed TV Up Running')
    	else:
        	print('Button Pressed TV Down')
    		time.sleep(.1)
		thread = Thread( target=startDown ).start()
        	print('Button Pressed TV Down Running')
	last_state = input_state
	lastTime = time.time();
    time.sleep(.1)
