#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test reading sensors table

import sqlite3

HOST = "chuck"
DB = '/home/reichler/telemetry.db'

with sqlite3.connect(DB, detect_types=sqlite3.PARSE_DECLTYPES) as con:
    cur = con.cursor()
    
    
    # read in ALL the sensor types
    try:
        cur.execute("SELECT * FROM sensors;")
        sensors = cur.fetchall()
        sdict = {s[2]: s[0] for s in sensors}

        print "\nSensors registered in {} for ANY host:\n".format(DB)
        print "type \t Id"
        print "-------------"
        for k, v in sdict.iteritems():
            print k,'\t ', v
    except sqlite3.Error, e:
        print "Error: {}".format(e)
    
    # read in the sensor types for HOST
    try:
        cur.execute("SELECT * FROM sensors WHERE host='{}';".format(HOST))
        sensors = cur.fetchall()
        sdict = {s[2]: s[0] for s in sensors}
        print "\nSensors registered in {} for host '{}':\n".format(DB, HOST)
        print "type \t Id"
        print "-------------"
        for k, v in sdict.iteritems():
            print k,'\t ', v
    except sqlite3.Error, e:
        print "Error: {}".format(e)
