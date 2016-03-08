#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create the database file for telemetry. This could of course be easily done with just the
# SQlite command line tool, but for future refernce and parameterization...

import sqlite3
import sys

filename = '/home/reichler/telemetry.db'
datatable = 'telemetry'
sensortable = 'sensors'

# note the need for unicode string with the degree symbol. Yikes.
sensors = [('chuck', 'temp', "LM35 temperature sensor. Strongly affected by sunlight coming in through the window over Chuck. You'll see.", '1.0', u'°C'),
           ('chuck', 'light', "Light dependent resistor on the breadbord. Room lighting is shadowed by Chucks leaves.", "1.0", ''),
           ('chuck', 'soil', "Two aluminium sticks in the ground measuring resistance when pulsed by digital pin. Correlates with moisture in ground.", '1.0', ''),
           ('none', 'dummy', "Dummy sensor to test selectivity.", '1.0', '')
           ]

with sqlite3.connect('{}'.format(filename), detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:
    try:
        cur = con.cursor()
        # Check sqlite version
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        print "SQlite version {}".format(data[0])

        # Create the table with sensor descriptions
        cur.execute("""CREATE TABLE IF NOT EXISTS {st}(Id INTEGER PRIMARY KEY, host TEXT, type TEXT, description TEXT, factor REAL, unit TEXT);""".format(st=sensortable))
        con.commit()

        # Create the table for data
        cur.execute("""CREATE TABLE IF NOT EXISTS {tn}(Id INTEGER PRIMARY KEY, timestamp REAL, type INTEGER, value REAL);""".format(tn=datatable))
        con.commit()
        
        cur.executemany("""INSERT INTO {st}(host, type, description, factor, unit) VALUES(?, ?, ?, ?, ?)""".format(st=sensortable), sensors)
    except sqlite3.Error, e:
        print "Error: {}".format(e)
        sys.exit(1)
    else:
        print "Successfully created {db} with tables {dt} and {st}.".format(db=filename, dt=datatable, st=sensortable)

if __name__ == '__main__':
    pass