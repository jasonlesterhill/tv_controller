from threading import Thread
import os
import sys
import math
import smbus
import time
import datetime

processId = str(os.getpid())
f = open('/tmp/tv_dir', 'w')
f.write("{\"dir\": \"tvDown\", \"pid\": " + processId + "}\n")
f.close()
#sys.stdout = open('/tmp/tv_log_' + processId, 'w')


bus = smbus.SMBus(1)

def readAngleRaw(address):
	count = 0;
	while True:
		try:
			dataBuf = bus.read_i2c_block_data(address, 50, 6)
			x1 = dataBuf[0]
			x2 = dataBuf[1]
			y1 = dataBuf[2]
			y2 = dataBuf[3]
			z1 = dataBuf[4]
			z2 = dataBuf[5]

			x = (x2 << 8 | x1);
			y = (y2 << 8 | y1);
			z = (z2 << 8 | z1);
		
			if x > 0x7fff:
				x = (0x10000 - x) * -1
			
			if y > 0x7fff:
				y = (0x10000 - y) * -1
			
			if z > 0x7fff:
				z = (0x10000 - z) * -1
			
        		if z == 0:
				z = .000001
			#//print "angle: " + str( math.degrees(math.atan(float(x)/float(z))))
			return math.degrees(math.atan(float(x)/float(z)))
		except (IOError):
			print "IO Error -- retry"
			count += 1;
			if(count > 5):
				raise
def readAngleTV():
	address = 0x1d
	bus.write_byte_data(address, 0x2d, 0x8)
	bus.write_byte_data(address, 0x2c, 0xd)
	bus.write_byte_data(address, 0x31, 0x0)
	data = 0;
	count = 0;
	while count < 10:
		#//time.sleep(.001)
		data += readAngleRaw(address);
		count += 1
	data = data / 10;
        percent = 1.0 - data / 68.0
	return percent;

def readAngleShelf():
	address = 0x53
	bus.write_byte_data(address, 0x2d, 0x8)
	bus.write_byte_data(address, 0x2c, 0xd)
	bus.write_byte_data(address, 0x31, 0x0)
	data = 0;
	count = 0;
	while count < 10:
		raw = readAngleRaw(address);
        	if raw < -25.0:
			raw = raw + 180.0
		data += raw
		#//time.sleep(.001)
		count += 1
	deg = data / 10;
	deg -= 5.5
       	percent = deg / 115.0
	return percent;

count = 0
start = time.time()
print "time : " + str((time.time()))

while True:
	start = time.time()
	tv = readAngleTV()
	shelf = readAngleShelf()
	print "starting status tv:\t" + str(tv) + ", shelf:" + str(shelf) +  " time : " + str((time.time() - start))
