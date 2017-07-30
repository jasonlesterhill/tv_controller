from threading import Thread
import os
import sys
import math
import smbus
import time
import datetime
import RPi.GPIO as GPIO


ADS1x15_POINTER_CONVERSION     = 0x00
ADS1x15_POINTER_CONFIG         = 0x01
ADS1x15_POINTER_LOW_THRESHOLD  = 0x02
ADS1x15_POINTER_HIGH_THRESHOLD = 0x03

bus = smbus.SMBus(1)

print "initializing pins"
GPIO.setmode(GPIO.BOARD)
# Shelf
GPIO.setup(32, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)

start = time.time()


def initCurrent():
	target = [0b11110010, 0b10000011];
        bus.write_i2c_block_data(0x48, ADS1x15_POINTER_CONFIG, target)
        time.sleep(0.2)

def readCurrent():
	dataBuf = bus.read_i2c_block_data(0x48, ADS1x15_POINTER_CONVERSION, 2)
        time.sleep(0.05)
	x = (dataBuf[0] << 8 | dataBuf[1]);
	if x > 0x7fff:
		x = (0x10000 - x) * -1
	print "Value: " + str(x) + " " + str(time.time() - start)
	return x;


def openShelf1Sec():
	initCurrent();
	print "ON";
	GPIO.output(35, GPIO.LOW)
	GPIO.output(32, GPIO.HIGH)
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	readCurrent();
	GPIO.output(32, GPIO.LOW)
	print "OFF";
	readCurrent();
	readCurrent();

openShelf1Sec();
GPIO.cleanup();

