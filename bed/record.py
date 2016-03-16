from __future__ import division
import time
import serial
import csv
from datetime import datetime as dt

DEBUG = True


def timestamp():
    ts = dt.now()
    return time.mktime(ts.timetuple())+(ts.microsecond/1e6)

bufsize = 1 if DEBUG else -1
with open('db/rec.csv', 'a', bufsize) as f:
    writer = csv.writer(f)
    with serial.Serial('/dev/ttyUSB0', 57600, timeout=1.0) as ser:
        # Empty whatever is in the buffer
        ser.flushInput()
        while ser.inWaiting():
            ser.read()
        
        while True:
            values = []
	    ser.write('a')
		while ser.inWaiting():
		line = ser.readline().strip()
		print line
		time.sleep(100)
            writer.writerow([timestamp(), line])
