from threading import Thread
import os
import sys
import math
import smbus
import time
import RPi.GPIO as GPIO
import datetime

processId = str(os.getpid())
f = open('/tmp/tv_dir', 'w')
f.write("{\"dir\": \"tvDown\", \"pid\": " + processId + "}\n")
f.close()
sys.stdout = open('/tmp/tv_log_' + processId, 'w')


bus = smbus.SMBus(1)
address = 0x53
address = 0x1d
address = 0x53

print "initializing pins"
GPIO.setmode(GPIO.BOARD)
# Shelf
GPIO.setup(32, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)

def closeShelf1Sec():
	GPIO.output(35, GPIO.HIGH)
	GPIO.output(32, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(32, GPIO.LOW)

def openShelf1Sec():
	GPIO.output(35, GPIO.LOW)
	GPIO.output(32, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(32, GPIO.LOW)
	

try:
	closeShelf1Sec()
except (KeyboardInterrupt):
	print "keyboard abort"
except:
	print "unknown abort"
	abort = True
	movingTV = False;
	GPIO.output(32, GPIO.LOW)
	GPIO.cleanup()
	raise

print "Done Moving"
movingTV = False;
GPIO.output(32, GPIO.LOW)
GPIO.cleanup()
abort = True
