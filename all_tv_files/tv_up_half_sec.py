from threading import Thread
import os
import sys
import math
import smbus
import time
import RPi.GPIO as GPIO
import datetime

ADS1x15_POINTER_CONVERSION     = 0x00
ADS1x15_POINTER_CONFIG         = 0x01
ADS1x15_POINTER_LOW_THRESHOLD  = 0x02
ADS1x15_POINTER_HIGH_THRESHOLD = 0x03


bus = smbus.SMBus(1)
address = 0x53
address = 0x1d
address = 0x53

print "initializing pins"
GPIO.setmode(GPIO.BOARD)
# Shelf
GPIO.setup(32, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
# TV
GPIO.setup(33, GPIO.OUT) 
GPIO.setup(31, GPIO.OUT) 
tvPWM = GPIO.PWM(33, 3000)  

global tv;
global shelf;
shelf = -1000
global movingShelf;
global movingTV;
global tvSlowing;
global abort;
global direction;
global start;
abort = False;
movingTV = False
movingShelf = False
tvSlowing = False
direction = ""

def initCurrent():
	target = [0b11110010, 0b10000011];
	bus.write_i2c_block_data(0x48, ADS1x15_POINTER_CONFIG, target)
	time.sleep(0.2)
 
def readCurrent():
	dataBuf = bus.read_i2c_block_data(0x48, ADS1x15_POINTER_CONVERSION, 2)
	x = (dataBuf[0] << 8 | dataBuf[1]);
	if x > 0x7fff:
		x = (0x10000 - x) * -1
	print "Value: " + str(x) + " " + str(time.time() - start)
	return x;

def moveTV(closing):
	global start;
	initCurrent();
	start = time.time();
        if (closing == 1):
		GPIO.output(31, GPIO.LOW)
		print "closing"
	else: 
		GPIO.output(31, GPIO.HIGH)
		print "opening"
       	tvPWM.start(70)
	count = 0;
 	while ((time.time() - start) < .52):
		time.sleep(0.01)
		readCurrent();	
		count = count + 1;
	tvPWM.stop();



try:
	moveTV(0)
except (KeyboardInterrupt):
	print "keyboard abort"
except:
	print "unknown abort"
	abort = True
	movingTV = False;
	tvPWM.stop();
	GPIO.output(32, GPIO.LOW)
	GPIO.cleanup()
	raise

print "Done Moving"
movingTV = False;
tvPWM.stop();
GPIO.output(32, GPIO.LOW)
GPIO.cleanup()
abort = True
