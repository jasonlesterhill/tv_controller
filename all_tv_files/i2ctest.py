import sys
import math
import smbus
import time
import RPi.GPIO as GPIO
import datetime



bus = smbus.SMBus(1)
address = 0x53
address = 0x1d
address = 0x53

GPIO.setmode(GPIO.BOARD)
# Shelf
GPIO.setup(32, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
shelfPWM = GPIO.PWM(32, 3000)  
# TV
GPIO.setup(33, GPIO.OUT) 
GPIO.setup(31, GPIO.OUT) 
tvPWM = GPIO.PWM(33, 3000)  

def readAngleTV():
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
	deg = math.degrees(math.atan(float(x)/float(z))) + .8
        percent = 1.0 - deg / 73.0
	#print "tv," +str(percent) + "," + str(x) + "," + str(y) + "," + str(z)
	return percent;

def readAngleShelf():
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
        if deg < -45.0:
		deg = deg + 180.0
	deg -= 5.5
        percent = deg / 115.0
	#print "shelf," +str(percent) + "," + str(x) + "," + str(y) + "," + str(z)
	return percent;

def targetShelf(target):
	print "moving shelf to target: " + str(target)
        shelf = readAngleShelf()
	print "shelf at: " + str(shelf)
	closing = 1
        if (shelf > target):
		GPIO.output(35, GPIO.HIGH)
		print "closing"
	else: 
		GPIO.output(35, GPIO.LOW)
		print "opening"
		closing = 0
        shelfPWM.start(100)
	count = 0
	delta_miss = 0
	while((delta_miss < 4) and ((shelf < target and closing == 0) or (shelf > target and closing == 1))):
		if (abs(shelf - target) < .05):
			print "Slowing: " + str(abs(shelf - target))
			shelfPWM.ChangeDutyCycle(60.0)
		time.sleep(0.25)
		lastShelf = shelf
        	shelf = readAngleShelf()
		delta = abs(shelf - lastShelf)
		if delta < .005:
			delta_miss = delta_miss + 1
		else:
			delta_miss = 0
		print "Shelf: " + str(shelf) + " delta = " + str(delta) + " " +  str(datetime.datetime.now().time())
		count = count + 1 
	shelfPWM.stop()

def targetTV(target):
	print "moving TV to target: " + str(target)
        tv = readAngleTV()
	print "tv at: " + str(tv)
	closing = 1
        if (tv > target):
		GPIO.output(31, GPIO.LOW)
		print "closing"
	else: 
		GPIO.output(31, GPIO.HIGH)
		print "opening"
		closing = 0
        tvPWM.start(100)
	count = 0
	delta_miss = 0
	while((delta_miss < 4) and count < 100 and ((tv < target and closing == 0) or (tv > target and closing == 1))):
		if (abs(tv - target) < .05):
			print "Slowing: " + str(abs(tv - target))
			tvPWM.ChangeDutyCycle(70.0)
		time.sleep(0.5)
		lastTV = tv
        	tv = readAngleTV()
		delta = abs(tv - lastTV)
		if delta < .01:
			delta_miss = delta_miss + 1
		else:
			delta_miss = 0
		print "TV: " + str(tv) + " delta = " + str(delta) + " " +  str(datetime.datetime.now().time())
		count = count + 1 
	print delta_miss
	tvPWM.stop()

tv = readAngleTV()
shelf = readAngleShelf()
print "status:\t" + str(tv) + ",\t" + str(shelf)

shelfTarget = float(sys.argv[1])
tvTarget = float(sys.argv[2])
finalShelfTarget = float(sys.argv[3])
if (shelfTarget >= 0 and shelfTarget <= 1.0 and (readAngleTV() > .98 or readAngleTV() < .02)):
	targetShelf(shelfTarget)
else:
	print "TV not in position to move shelf."
if (tvTarget >= 0 and tvTarget <= 1.0 and readAngleShelf() > .98):
	targetTV(tvTarget)
else:
	print "Shelf not in position to move tv."
if (finalShelfTarget >= 0 and finalShelfTarget <= 1.0 and (readAngleTV() > .98 or readAngleTV() < .02)):
	targetShelf(finalShelfTarget)
else:
	print "TV not in position to move shelf."

shelfPWM.stop();
tvPWM.stop();
GPIO.cleanup()
