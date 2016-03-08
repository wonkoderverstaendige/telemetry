#!/usr/bin/env python
import datetime
import time
import serial
import sqlite3
import sys

HOST = "chuck"
DB = '/home/reichler/telemetry.db'
SER = '/dev/ttyACM0'
WRITE_TO_DB = True
INTERVAL = 5.000

# , detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
# allows parsing of datetime into and from the database if column name is "timestamp"
with serial.Serial(SER, 57600, timeout=10.0) as ser, \
     sqlite3.connect(DB, detect_types=sqlite3.PARSE_DECLTYPES) as con:

    cur = con.cursor()
    
    # clean up whatever Arduino has sent so far
    ser.flushInput()

    # Read in sensors registered for host
    cur.execute("SELECT * FROM sensors WHERE host='{}';".format(HOST))
    sensors = {s[2]: s[0] for s in cur.fetchall()}
    print "\nSensors registered in {} for host '{}':\n".format(DB, HOST)
    print "type \t Id"
    print "-------------"
    for k, v in sensors.iteritems():
        print k,'\t ', v

    # main loop gathering data
    while True:
        ser.write('a')
        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple()) + now.microsecond*1e-6
        time.sleep(0.25)
        readings = []
        while ser.inWaiting():
            try:
                data = ser.readline().rstrip().split(':')
                readings.append((timestamp, sensors[data[0]], float(data[1])))  
            except KeyError, e:
                print "Sensor not found: {}".format(e)
        
        if WRITE_TO_DB:
            try:
                cur.executemany("""INSERT INTO telemetry(timestamp, type, value) VALUES(?, ?, ?)""", readings)
                con.commit()
            except sqlite3.Error, e:
                print "Error: {}".format(e)
        
        time.sleep(INTERVAL-0.25)

if __name__ == '__main__':
    pass
