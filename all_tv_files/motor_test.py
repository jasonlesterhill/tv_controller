import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

p = GPIO.PWM(32, 3000)  # channel=12 frequency=50Hz
p.start(0)

p.ChangeDutyCycle(80.0)
print "wait"
time.sleep(0.5)
print "done"
p.ChangeDutyCycle(0)
p.stop()
GPIO.cleanup()
