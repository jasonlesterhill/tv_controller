import time
import os

count = 0

while count < 256:
	cmd= "irsend SEND_ONCE  Vizio TEST_" + str(count)
	print cmd
        os.system(cmd)
	time.sleep(.5)
	count += 1
	if (count == 9):
		count = 10;
	if (count == 43):
		count = 44;
