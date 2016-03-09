#!/usr/bin/env python

import sqlite3

with sqlite3.connect('db/telemetry.db') as con:
    cur = con.cursor()
    cur.execute('DELETE FROM telemetry WHERE rowid NOT IN ' \
            '(SELECT MIN(rowid) FROM telemetry GROUP BY timestamp, type);')
    con.commit()

