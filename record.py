#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        # wait for the end of the first line
        ser.readline()


def loop(writer, ser):
    while True:
        try:
            line = ser.readline()
            sensor, value = line.rstrip().split(':')
            value = float(value)
        except (KeyError, ValueError), error:
            pass
            # print error
        else:
            row = [timestamp(), sensor, '{:.2f}'.format(value)]
            print row
            writer.writerow(row)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save serial data to csv file.")
    parser.add_argument('-p', '--port', help='Serial port path', default=SERIAL_PATH)
    parser.add_argument('-b', '--baud', help='Serial baud rate', default=57600)
    parser.add_argument('-r', '--timeout', help='Serial baud rate', default=10.0)
    cli_args = parser.parse_args()

    assert os.path.exists(SERIAL_PATH)
    assert os.path.exists(LOCAL_DB_PATH)

    buffer_size = 1 if DEBUG else 4*2**10
    filename = SENSOR_HOST + time.strftime('_%Y-%m-%d') + '.csv'
    print os.path.join(LOCAL_DB_PATH, filename)
    with open(os.path.join(LOCAL_DB_PATH, filename), 'a', buffer_size) as f:
        csv_writer = csv.writer(f)
        with serial.Serial(cli_args.port, cli_args.baud, timeout=cli_args.timeout) as serial_port:
            clear_serial(serial_port)
            loop(csv_writer, serial_port)
