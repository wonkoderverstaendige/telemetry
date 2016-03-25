from __future__ import division
import time
import os
import serial
import csv
from datetime import datetime as dt
from util.misc import get_local_config

DEBUG = True
SERIAL_PATH = '/dev/ttyACM0'
LOCAL_CONFIG = get_local_config()
SENSOR_HOST = LOCAL_CONFIG['host']['node']
LOCAL_DB_PATH = LOCAL_CONFIG['paths']['db']


def timestamp():
    t = dt.now()
    return time.mktime(t.timetuple())+(t.microsecond/1e6)


def clear_serial(ser):
    # Empty whatever is still stuck in the buffer
    ser.flushInput()
    while ser.inWaiting():
        ser.read()


def loop(writer, ser):
    while True:
        try:
            sensor, value = ser.readline().rstrip().split(':')
            value = float(value)
        except (KeyError, ValueError), error:
            print error
        else:
            row = [timestamp(), sensor, value]
            print row
            writer.writerow(row)


if __name__ == "__main__":
    assert os.path.exists(SERIAL_PATH)
    assert os.path.exists(LOCAL_DB_PATH)

    buffer_size = 1 if DEBUG else 4*2**10
    filename = SENSOR_HOST + time.strftime('_%Y-%m-%d') + '.csv'
    print os.path.join(LOCAL_DB_PATH, filename)
    with open(os.path.join(LOCAL_DB_PATH, filename), 'a', buffer_size) as f:
        csv_writer = csv.writer(f)
        with serial.Serial(SERIAL_PATH, 57600, timeout=1.0) as serial_port:
            clear_serial(serial_port)
            loop(csv_writer, serial_port)
