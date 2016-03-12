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
    with serial.Serial('/dev/ttyACM0', 57600, timeout=1.0) as ser:
        # Empty whatever is in the buffer
        ser.flushInput()
        while ser.inWaiting():
            ser.read()
        
        while True:
            values = []
            for _ in range(50):
                line = ser.readline().strip()
                try:
                    values.append(int(line))
                except ValueError:
                    print str(dt.now()), 'NaN:', line
            print timestamp(), min(values), max(values)
            writer.writerow([timestamp(), min(values), max(values)])
