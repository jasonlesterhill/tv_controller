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

def monitorPosition():
	global abort;
	global tv;
	global shelf;
	global start;
	start = time.time();
	while abort == False:
        	tv = readAngleTV()
        	shelf = readAngleShelf()
		writeStatus();
		f = open('/tmp/tv_dir', 'r')
		dirData = f.read();
		f.close();
		if 'stop' in dirData or not processId in dirData:
			abort = True
			print "aborting movement"
		#print "status tv:\t" + str(tv) + ", shelf:" + str(shelf)
		time.sleep(.05)
	writeStatus();
	

def readAngleRaw(address, xOrNotY):
	count = 0;
	while True:
		try:
			dataBuf = bus.read_i2c_block_data(address, 50, 6)
			bus.read_byte_data(address, 0)
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
			if xOrNotY:
				print "Using X"
				return math.degrees(math.atan(float(x)/float(z)))
			print "Using Y"
			return math.degrees(math.atan(-float(y)/float(z)))
		except (IOError):
			print "IO Error -- retry"
			count += 1;
			if(count > 5):
				raise
def readAngleTV():
	address = 0x53
	bus.write_byte_data(address, 0x2d, 0x8)
	bus.write_byte_data(address, 0x31, 0x0)
	data = 0;
	count = 0;
	while count < 10:
		data += readAngleRaw(address, True);
		count += 1
	data = data / 10;
	print "tv deg: " + str(data)
        percent = 1.0 - data / 68.0
	return percent;

def readAngleShelf():
	address = 0x1d
	bus.write_byte_data(address, 0x2d, 0x8)
	bus.write_byte_data(address, 0x31, 0x0)
	data = 0;
	count = 0;
	while count < 5:
		data += readAngleRaw(address, False);
		count += 1
	deg = data / 5;
	print "shelf deg: " + str(deg)
        if deg < -25.0:
		deg = deg + 180.0
	deg -= 5.5
       	percent = deg / 115.0
	return percent;

def readAngleShelf2():
	count = 0;
	while True:
		try:
        		address = 0x1d
			bus.write_byte_data(address, 0x2d, 0x8)
			bus.write_byte_data(address, 0x31, 0x0)
			bus.read_byte_data(address, 0)
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
			deg = math.degrees(math.atan(-1.0 * float(y)/float(z)));
        		if deg < -25.0:
					deg = deg + 180.0
			deg -= 5.5
        		percent = deg / 115.0
			#print "shelf," +str(percent) + "," + str(x) + "," + str(y) + "," + str(z) + "," + str(math.degrees(math.atan(-1.0 * float(y)/float(z))));
			return percent;
		except (IOError):
			print "IO Error -- retry"
			count += 1;
			if(count > 5):
				raise


count = 0
start = time.time()
while count < 10:
	tv = readAngleTV()
	shelf = readAngleShelf()
	print "starting status tv:\t" + str(tv) + ", shelf:" + str(shelf)
	shelf = readAngleShelf2()
	print "starting status tv:\t" + str(tv) + ", shelf:" + str(shelf)
	count += 1
print "time : " + str((time.time() - start) / count)
