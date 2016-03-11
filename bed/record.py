from __future__ import division
import time
import serial
import csv
from datetime import datetime as dt


def timestamp():
    ts = dt.now()
    return time.mktime(ts.timetuple())+(ts.microsecond/1e6)

with open('rec.csv', 'wa') as f:
    writer = csv.writer(f)
    with serial.Serial('/dev/ttyACM0', 57600, timeout=1.0) as ser:
        
        # Empty whatever is in the buffer
        ser.flushInput()
        while ser.inWaiting():
            ser.read()
        
        while True:
            values = []
            for _ in range(50):
                try:
                    line = ser.readline().strip()
                    values.append(int(line))
                except ValueError:
                    print str(dt.now()), 'NaN:', line
            print timestamp(), min(values), max(values)
            writer.writerow([timestamp(), min(values), max(values)])