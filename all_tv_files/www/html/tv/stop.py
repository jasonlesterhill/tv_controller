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
sys.stdout = open('/tmp/tv_log_stop_' + processId, 'w')

print "Stop Called...."
print "TV Motion Stopped " + str(time.time())
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
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
def wait():
	global abort;
	try:
		print "waiting for enter"
		sys.stdin.read(1);
	except:
		1
	abort = True;
	print "Done"

def writeStatus():
	f = open('/tmp/tv_stats', 'w')
	f.write("{ \"tv\": " + str(tv) + ", \"shelf\": " + str(shelf) + ", \"movingShelf\": " + str(movingShelf) +", \"movingTV\": " + str(movingTV) + ", \"duration\": " + str(time.time() - start) + ", \"pid\": " + str(processId) + ", \"direction\": \"" + str(direction) +"\"}\n")
	f.close()

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
	

def readAngleTV():
	count = 0;
	while True:
		try:
        		address = 0x53
			bus.write_byte_data(address, 0x2d, 0x8)
			bus.write_byte_data(address, 0x31, 0x0)
			bus.read_byte_data(address, 0)
			x1 = bus.read_byte_data(address, 50)
			x2 = bus.read_byte_data(address, 51)
			y1 = bus.read_byte_data(address, 52)
			y2 = bus.read_byte_data(address, 53)
			z1 = bus.read_byte_data(address, 54)
			z2 = bus.read_byte_data(address, 55)
		
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
			deg = math.degrees(math.atan(float(x)/float(z)))
        		percent = 1.0 - deg / 68.0
			#print "tv," +str(percent) + "," + str(x) + "," + str(y) + "," + str(z) + ", " + str(deg)
			return percent;
		except (IOError):
			print "IO Error -- retry"
			count += 1;
			if(count > 5):
				raise


def readAngleShelf():
	count = 0;
	while True:
		try:
        		address = 0x1d
			bus.write_byte_data(address, 0x2d, 0x8)
			bus.write_byte_data(address, 0x31, 0x0)
			bus.read_byte_data(address, 0)
			x1 = bus.read_byte_data(address, 50)
			x2 = bus.read_byte_data(address, 51)
			y1 = bus.read_byte_data(address, 52)
			y2 = bus.read_byte_data(address, 53)
			z1 = bus.read_byte_data(address, 54)
			z2 = bus.read_byte_data(address, 55)
		
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

def moveTV(target, closing, start):
	global tv
	global movingTV
	global tvSlowing
	print "TV motion: "  + str(movingTV) + " " + str(tv) + " " + str(target) + " " + str(closing)  + " " + str(start) + " " +  str(datetime.datetime.now().time())
	if start:
		if (abs(tv - target) < .02):
			movingTV = False;
			tvPWM.stop()
			print "TV NOT Moving"
			return False;
		print "Start Called"
	if(not ((tv < target and closing == 0) or (tv > target and closing == 1))):
		movingTV = False;
		tvPWM.stop()
		print "TV NOT Moving"
		return False
	if start:
		print "moving TV to target: " + str(target)
		print "tv at: " + str(tv)
		movingTV = True;
        	if (closing == 1):
			GPIO.output(31, GPIO.LOW)
			print "closing"
		else: 
			GPIO.output(31, GPIO.HIGH)
			print "opening"
        	tvPWM.start(100)
		tvSlowing = False;
	if (abs(tv - target) < .05 and not tvSlowing):
		print "Slowing: " + str(abs(tv - target))
		movingTV = True;
		tvSlowing = True;
		#tvPWM.ChangeDutyCycle(70.0)

	return True;

def moveShelf(target, closing):
       	global shelf
	#if not movingTV:
		#GPIO.output(32, GPIO.LOW)
	if(not ((shelf < target and closing == 0) or (shelf > target and closing == 1))):
		print "shelf NOT Moving"
		GPIO.output(32, GPIO.LOW)
		return False
	#GPIO.setup(32, GPIO.OUT)
	#GPIO.setup(35, GPIO.OUT)
       	if (closing == 1):
		GPIO.output(35, GPIO.HIGH)
	else: 
		GPIO.output(35, GPIO.LOW)
	GPIO.output(32, GPIO.HIGH)
	print "Shelf Moving: " + str(shelf) + " " + str(target) + " " +  str(datetime.datetime.now().time()) + " " + str(closing)
	return True;

thread = Thread( target=monitorPosition ).start()
while shelf == -1000:
	time.sleep(.1)
	print "waiting for init: " + str(shelf)

def tvDown():
	global tv
	global shelf
	global movingTV
	global movingShelf
	global direction
	direction = "Down"	
	f = open('/tmp/tv_dir', 'w')
	f.write("{\"dir\": \"tvDown\", \"pid\": " + processId + "}\n")
	f.close()
	
	print "status:\t" + str(tv) + ",\t" + str(shelf)
 	movingShelf = True	
 	movingTV = True	
	count = 0;
	if (tv > .05): #open shelf if TV not closed
		movingShelf = moveShelf(1, 0)
		print "stage 1"
		while movingShelf and (shelf < .30 or tv < .95) and not abort:
			print "movingShelf"
			time.sleep(.1)
			count += 1
			movingShelf = moveShelf(1, 0)
			print "down status:\t" + str(tv) + ",\t" + str(shelf)
		movingTV = moveTV(0, 1, True)
	print "stage 2"
	while (movingTV or movingShelf) and tv > .2 and not abort:
		print "(movingTV or movingShelf)"
		time.sleep(.2)
		count += 1
		movingTV &= moveTV(0, 1, False)
        	movingShelf = moveShelf(1, 0)
		print "down status 2:\t" + str(tv) + ",\t" + str(shelf) + " " + str(movingTV) + " " + str(movingShelf)
	
	movingTV = moveTV(0, 1, True)
	movingShelf = moveShelf(0, 1)
	print "stage 3"
	while (movingTV or movingShelf) and not abort:
		print "moving"
		time.sleep(.1)
		count += 1
		movingTV &= moveTV(0, 1, False)
        	movingShelf = moveShelf(0, 1)
		print "down status 3:\t" + str(tv) + ",\t" + str(shelf) + " " + str(movingTV) + " " + str(movingShelf)
	direction = "Done"	

def tvUp():
	global tv
	global shelf
	global movingTV
	global movingShelf
	global direction
	direction = "Up"	
	f = open('/tmp/tv_dir', 'w')
	f.write("{\"dir\": \"tvUp\", \"pid\": " + processId + "}\n")
	f.close()
	print "status:\t" + str(tv) + ",\t" + str(shelf)
 	movingShelf = True	
 	movingTV = True	
	count = 0;
	if (tv < .95): #open shelf if TV not already up
		movingShelf = moveShelf(1, 0)
		print "stage 1"
		while movingShelf and (shelf < .60) and not abort:
			print "movingShelf"
			time.sleep(.1)
			count += 1
			movingShelf = moveShelf(1, 0)
			print "status:\t" + str(tv) + ",\t" + str(shelf)
		movingTV = moveTV(1, 0, True)
	print "stage 2"
	while (movingTV or movingShelf) and tv < .49 and not abort:
		print "moving"
		time.sleep(.1)
		count += 1
		movingTV &= moveTV(1, 0, False)
        	movingShelf = moveShelf(1, 0)
		print "status 2:\t" + str(tv) + ",\t" + str(shelf) + " " + str(movingTV) + " " + str(movingShelf)
	
	movingTV = moveTV(1, 0, True)
	movingShelf = moveShelf(0, 1)
	print "stage 3"
	while (movingTV or movingShelf) and not abort:
		print "moving"
		time.sleep(.1)
		count += 1
		if movingTV: 
			movingTV = moveTV(1, 0, False)
        	movingShelf = moveShelf(0, 1)
		print "status 3:\t" + str(tv) + ",\t" + str(shelf) + " tv moving:" + str(movingTV) + " shelf moving:" + str(movingShelf)
	direction = "Done"	

def closeShelf():
	GPIO.output(35, GPIO.HIGH)
	GPIO.output(32, GPIO.HIGH)
	while shelf > .01:
		time.sleep(.1)
	GPIO.output(32, GPIO.LOW)
	print "Shelf Closed"

def openShelf():
	GPIO.output(35, GPIO.LOW)
	GPIO.output(32, GPIO.HIGH)
	while shelf > .01:
		time.sleep(.1)
	GPIO.output(32, GPIO.LOW)
	
#Thread( target=wait ).start()

try:
        tv = readAngleTV()
        shelf = readAngleShelf()
	print "starting status tv:\t" + str(tv) + ", shelf:" + str(shelf)
	print "TV Stopped."
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
