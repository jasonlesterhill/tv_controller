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

print "TV Motion Started " + str(time.time())
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

def initCurrent():
        target = [0b11110010, 0b10000011];
        ADS1x15_POINTER_CONFIG         = 0x01
        bus.write_i2c_block_data(0x48, ADS1x15_POINTER_CONFIG, target)
        time.sleep(0.2)

def readCurrent():
        ADS1x15_POINTER_CONVERSION     = 0x00
        dataBuf = bus.read_i2c_block_data(0x48, ADS1x15_POINTER_CONVERSION, 2)
        x = (dataBuf[0] << 8 | dataBuf[1]);
        if x > 0x7fff:
                x = (0x10000 - x) * -1
        print "ADC CurrentValue: " + str(x) + " " + str(time.time() - start)
        return x;


def isValid(tvReading, shelfReading):
	if(tvReading < 0.04 or tvReading > .98):
		return True;
	if(shelfReading > .98):
		return True;
	if(shelfReading < -tvReading * 1.35 + 1.65 and tvReading > .5):
		print "isValid Fail: " + str(shelfReading) + " " + str(-tvReading * 1.35 + 1.75)
		return False;
	if(shelfReading < tvReading * 1.3 + 0.55 and tvReading < .5):
		print "isValid Fail 2: " + str(shelfReading) + " " + str(tvReading * 1.3 + 0.55)
		return False;
	return True;

def isValidCurrent(status):
	return True;
	if (not status['tv_moving']):
		return status['current'] < 2500;
	global direction

	if (direction == 'Up'):
		return status['current'] < min(19000.0*status['tv']+9000.0, 24000.0);

	# Assume TV Down
	return status['current'] < max(8000.0,-23000.0*status['tv']+15000.0)


def writeStatus():
	f = open('/tmp/tv_stats', 'w')
	f.write("{ \"tv\": " + str(tv) + ", \"shelf\": " + str(shelf) + ", \"movingShelf\": " + str(movingShelf) +", \"movingTV\": " + str(movingTV) + ", \"duration\": " + str(time.time() - start) + ", \"pid\": " + str(processId) + ", \"direction\": \"" + str(direction) +"\"}\n")
	f.close()

def monitorPosition():
	global abort;
	global tv;
	global shelf;
	global start;
	global status;

	status = {}
	start = time.time();
        tv = readAngleTV()
        shelf = readAngleShelf()
	lastTv = tv
	lastShelf = shelf
	shelfAvgDelta = 0;
	tvAvgDelta = 0;
	time.sleep(.05)
	movingShelfCount = 0;
	movingTvCount = 0;
	status['current'] = readCurrent();
	while abort == False:
        	newTv = readAngleTV()
		if (abs(newTv - lastTv) < .1):
			tvAvgDelta = (newTv - lastTv) * .025 + tvAvgDelta * .975;
		print "TV Delta: " + str((newTv - tv)) + " " + str(newTv) + " " + str(tv) + " " + str(tvAvgDelta)
		if abs(newTv - lastTv) > .13:
			print "TV Discarding bogus reading..." + str(newTv)
		if abs(newTv - lastTv) > .03:
			tv = tv * .95 + newTv * 0.05
			print "TV Smoothing..." + str(tv)
		else:
			tv = newTv
		lastTv = newTv;
        	newShelf = readAngleShelf()
		if (abs(newShelf - lastShelf) < .1):
			shelfAvgDelta = (newShelf - lastShelf) * .025 + shelfAvgDelta * .975;
		print "Shelf Delta: " + str((newShelf - shelf)) + " " + str(newShelf) + " " + str(shelf) + " " + str(shelfAvgDelta);
		if abs(newShelf - lastShelf) > .13:
			print "Shelf Discarding bogus reading..." + str(newShelf)
		if abs(newShelf - shelf) > .06:
			shelf = shelf * .95 + newShelf * 0.05
			print "Shelf Smoothing..." + str(shelf)
		else:
			shelf = newShelf
		lastShelf = newShelf;
		print "Shelf Speed: " + str(shelfAvgDelta * 1000) + " TV Speed: " + str(tvAvgDelta * 1000) + " " + str(movingShelf) + " " + str(movingTV)

		status['time'] = time.time()
		status['duration'] = time.time() - start
		status['tv_speed'] = tvAvgDelta;
		status['tv_moving'] = movingTV;
		status['shelf_speed'] = shelfAvgDelta;
		status['shelf_moving'] = movingShelf;
		status['tv'] = tv;
		status['current_raw'] = readCurrent();
		status['current'] = min(status['current_raw'], status['current_raw'] * .2 + status['current'] * .8);
		status['last_reading_tv'] = newTv;
		status['shelf'] = shelf;
		status['last_reading_shelf'] = newShelf;
		print 'Current Status:', str(status)
		writeStatus();
		f = open('/tmp/tv_dir', 'r')
		dirData = f.read();
		f.close();
		if 'stop' in dirData or not processId in dirData:
			abort = True
			print "aborting movement"
		if (movingShelf):
			movingShelfCount += 1 
		else:
			movingShelfCount = 0
		if (movingTV):
			movingTvCount += 1
		else:
			movingTvCount = 0
		duration = time.time() - start
		print "TV Count: " + str(movingTvCount)	 +  " " + str(duration)
		if (movingShelfCount > 60 and abs(shelfAvgDelta) < .0005) or (movingShelfCount > 30 and abs(shelfAvgDelta) < .0003):
			abort = True
			print "aborting shelf stalled movement " + str(movingShelfCount) + " " + str(abs(shelfAvgDelta))
		if ((movingTvCount > 60 and abs(tvAvgDelta) < .0005) or (movingTvCount > 20 and abs(tvAvgDelta) < .0002)):
			abort = True
			print "aborting tv stalled movement " + str(movingTvCount) + " " + str(abs(tvAvgDelta))
		if (duration > 60.0):
			abort = True
			print "aborting tv duration > 60 s"
		if (not isValid(tv, shelf)):
			abort = True	
			print "aborting movement, invalid TV, Shelf combo: " + str(tv) + " " + str(shelf)
		if (not isValidCurrent(status)):
			abort = True	
			print "aborting movement, invalid Current";
		time.sleep(.05)
	writeStatus();
	
def readAngleRaw(address, xOrNotY):
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
			if xOrNotY:
				return math.degrees(math.atan(float(x)/float(z)))
			return math.degrees(math.atan(-float(y)/float(z)))
		except (IOError):
			print "IO Error -- retry"
			count += 1;
			if(count > 5):
				raise
def readAngleTV():
	address = 0x53
	bus.write_byte_data(address, 0x2c, 0xa)
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
	bus.write_byte_data(address, 0x2c, 0xa)
	bus.write_byte_data(address, 0x2d, 0x8)
	bus.write_byte_data(address, 0x31, 0x0)
	data = 0;
	count = 0;
	while count < 5:
		raw = readAngleRaw(address, False);
        	if raw < -25.0:
			raw = raw + 180.0
		data += raw
		count += 1
	deg = data / 5;
	print "shelf deg: " + str(deg)
	deg -= 5.5
       	percent = deg / 115.0
	return percent;

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
        	if (closing == 1):
			GPIO.output(31, GPIO.LOW)
			print "closing"
		else: 
			GPIO.output(31, GPIO.HIGH)
			print "opening"
        	tvPWM.start(100)
		movingTV = True;
		tvSlowing = False;
	#if (abs(tv - target) < .05 and not tvSlowing):
		#print "Slowing: " + str(abs(tv - target))
		#movingTV = True;
		#tvSlowing = True;
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
 	movingTV = False	
	count = 0;
	if (tv > .05): #open shelf if TV not closed
		movingShelf = moveShelf(1, 0)
		print "stage 1"
		while movingShelf and (shelf < .30) and not abort:
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
	
	movingTV = moveTV(0, 1, not movingTV)
	movingShelf = moveShelf(0, 1)
	print "stage 3"
        os.system("irsend SEND_ONCE  Vizio POWER_OFF")
	while (movingTV or movingShelf) and not abort:
		print "moving"
		print "sending power off"
		time.sleep(.1)
		count += 1
		movingTV &= moveTV(0, 1, False)
        	movingShelf = moveShelf(0, 1)
		print "down status 3:\t" + str(tv) + ",\t" + str(shelf) + " " + str(movingTV) + " " + str(movingShelf) + " time:" + str(time.time())
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
	count = 0;
 	movingTV = False	
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
	if not abort:
		print "sending power on"
        	os.system("irsend SEND_ONCE  Vizio POWER_ON")
	print "stage 2"
	while (movingTV or movingShelf) and tv < .69 and not abort:
		print "moving"
		time.sleep(.1)
		count += 1
		movingTV &= moveTV(1, 0, False)
        	movingShelf = moveShelf(1, 0)
		print "status 2:\t" + str(tv) + ",\t" + str(shelf) + " " + str(movingTV) + " " + str(movingShelf) + " time:" + str(time.time())
	
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
		print "status 3:\t" + str(tv) + ",\t" + str(shelf) + " tv moving:" + str(movingTV) + " shelf moving:" + str(movingShelf) + " time:" + str(time.time())
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
	

try:
	initCurrent();
        tv = readAngleTV()
        shelf = readAngleShelf()
	print "starting status tv:\t" + str(tv) + ", shelf:" + str(shelf)
	direction = float(sys.argv[1])
	if direction > .5:
		tvUp()
		print "Done TV Up."
	else:
		tvDown()
		print "Done TV Down."
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
