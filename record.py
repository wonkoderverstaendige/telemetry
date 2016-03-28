#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: Watchdog, throwing error when nothing was received for a while
# TODO: Error handling when serial connection drops out. Attempt reconnecting.
from __future__ import division
import os
import serial
import csv
from datetime import datetime as dt
from util.misc import get_local_config, timestamp, iso_week, iso_year

DEBUG = False
SERIAL_PATH = '/dev/ttyACM0'
LOCAL_CONFIG = get_local_config()
SENSOR_HOST = LOCAL_CONFIG['host']['node']
LOCAL_DB_PATH = LOCAL_CONFIG['paths']['db']
FIELDNAMES = ['timestamp', 'sensor_str', 'value']


def record_loop(db_path, serial_port, debug=False):
    buffer_size = 1 if debug else 4*2**10
    while True:
        csv_name = "{year}_w{week:02}-{hostname}.csv"\
            .format(hostname=SENSOR_HOST,
                    year=iso_year(),
                    week=iso_week())
        csv_path = os.path.join(db_path, csv_name)
        current_week = iso_week()
        print "Recording to ", csv_path

        with open(csv_path, 'a', buffer_size) as f:
            csv_writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

            # A header is nice to quickly determine in the pipeline
            # later on if the sensor column is strings, or integer ids
            if not os.path.getsize(csv_path):
                csv_writer.writeheader()

            # Make a new file for every week, based in iso calendar
            # This might cause some issues later down the line with
            # how pandas handles week numbers, but the iso_to_gregorian
            # function from "util.misc" should help with that
            while iso_week() == current_week:
                    try:
                        line = serial_port.readline()
                        sensor, value = line.rstrip().split(':')
                        row = {'timestamp': timestamp(),
                               'sensor_str': sensor,
                               'value': '{:.2f}'.format(float(value))}
                    except ValueError as error:
                        if debug:
                            print error
                    else:
                        if debug:
                            print '{0} | {1: <8} | {2}'.format(
                                            dt.fromtimestamp(int(row['timestamp'])).strftime("%Y-%m-%d %H:%M"),
                                            row['sensor_str'],
                                            row['value'])
                            csv_writer.writerow(row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save serial data to csv file.")
    parser.add_argument('-p', '--port', help='Serial port path', default=SERIAL_PATH)
    parser.add_argument('-b', '--baud', help='Serial baud rate', default=57600)
    parser.add_argument('-r', '--timeout', help='Serial baud rate', default=120.0)
    parser.add_argument('--debug', action='store_true',
                        help='Enable debugging. Immediate writes to file.', default=DEBUG)
    cli_args = parser.parse_args()

    assert os.path.exists(LOCAL_DB_PATH)
    print "Serial device path:", cli_args.port
    assert os.path.exists(cli_args.port)

    with serial.Serial(cli_args.port, cli_args.baud, timeout=cli_args.timeout) as ser:
        ser.flushInput()
        record_loop(LOCAL_DB_PATH, ser, cli_args.debug)
