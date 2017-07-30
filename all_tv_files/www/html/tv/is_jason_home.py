

import os;


value = os.system("ping -c 1 192.168.1.13 > /tmp/j_home_log");
print value
if 0 == os.system("ping -c 1 192.168.1.14 > /tmp/j_home_log"):
	print "Jason Is Home"
else:
	print "Jason Is Not Home"
