#!/usr/bin/env python
# -*- coding: utf-8 -*-
# test reading sensors table

import sqlite3
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check sensors in database of a node")
    parser.add_argument('db', help='Path to sqlite3 database file')
    parser.add_argument('-n', '--node', help='Node name', default=None)
    args = parser.parse_args()

    with sqlite3.connect(args.db, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        # read in ALL the sensor types
        try:
            query = "SELECT * FROM sensors"
            if args.node:
                query + "WHERE host='{}'".format(args.node)
            cur.execute(query)
            sensors = {s[0]: s[2] for s in cur.fetchall()}

            print "Id\ttype"
            print "-------------"
            for k, v in sensors.iteritems():
                print '{}\t{}'.format(k, v)
        except sqlite3.Error, e:
            print "Error: {}".format(e)
