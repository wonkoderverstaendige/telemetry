#!/usr/bin/env python

import sqlite3

with sqlite3.connect('db/telemetry.db') as con:
    cur = con.cursor()

    # Check file consistency
    assert(cur.execute('pragma integrity_check').fetchone()[0]==u'ok')
    print "Integrity OK!"

    # Check for duplicates
    duplicates = cur.execute('SELECT * FROM telemetry WHERE rowid NOT IN ' \
                      '(SELECT MIN(rowid) FROM telemetry GROUP BY timestamp, type);').fetchall()
    if duplicates:
        print duplicates
    assert(not duplicates)
    print "No duplicate rows!"
