from __future__ import division
import time
import serial
import csv
from datetime import datetime as dt

DEBUG = True


def timestamp():
    ts = dt.now()
    return time.mktime(ts.timetuple())+(ts.microsecond/1e6)

buffer_size = 1 if DEBUG else 4*2**10
with open('db/rec.csv', 'a', buffer_size) as f:
    writer = csv.writer(f)
    with serial.Serial('/dev/ttyUSB0', 57600, timeout=1.0) as ser:
        # Empty whatever is in the buffer
        ser.flushInput()
        while ser.inWaiting():
            ser.read()
        
        while True:
            data = {'temp': [],
                    'strain': []}
            for n in range(300):
                ser.write('a')
                time.sleep(.100)
                while ser.inWaiting():
                    try:
                        sensor, value = ser.readline().rstrip().split(':')
                        value = float(value)
                        data[sensor].append(value)
                    except (KeyError, ValueError),  error:
                        print error
            for key, values in data.items():
                ts = timestamp()
                if key == 'strain':
                    hi = [ts, 'strain_hi', max(values)]
                    lo = [ts, 'strain_lo', min(values)]
                    print hi, '\n', lo
                    writer.writerows([hi, lo])
                else:
                    row = [ts, key, sum(values)*1./len(values)]
                    print row
                    writer.writerow(row)

