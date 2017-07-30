from threading import Thread
import os
import sys
import math
import smbus
import time
import datetime

ADS1x15_POINTER_CONVERSION     = 0x00
ADS1x15_POINTER_CONFIG         = 0x01
ADS1x15_POINTER_LOW_THRESHOLD  = 0x02
ADS1x15_POINTER_HIGH_THRESHOLD = 0x03

bus = smbus.SMBus(1)


def readCurrent():
	address = 0x48

        #self._device.writeList(ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
	target = [0b11110100, 0b10000011];
	print "{0:b}".format(target[0])
	print "{0:b}".format(target[1])
        bus.write_i2c_block_data(address, ADS1x15_POINTER_CONFIG, target)

        time.sleep(0.2)
	read = 2;
	dataBuf = bus.read_i2c_block_data(address, ADS1x15_POINTER_CONVERSION, 2)
	#dataBuf = bus.read_i2c_block_data(address, ADS1x15_POINTER_CONFIG, 2)

	count = 0;
	while count < read:
		print str(dataBuf[count]);
		print "{0:b}".format(dataBuf[count])
		count += 1
	x = (dataBuf[0] << 8 | dataBuf[1]);
	if x > 0x7fff:
		x = (0x10000 - x) * -1
	print "Value: " + str(x);


readCurrent();
