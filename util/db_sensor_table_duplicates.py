#!/usr/bin/env python
# Checks if the table contains duplicate entries, i.e. multiple entries of the same sensor type
# with the same time stamp. Happened with older versions of gather.py, where the same sensor sent
# multiple values during the request window.

import os
import sqlite3
import argparse


def count_duplicates(cursor, table):

    cursor.execute('SELECT COUNT(*) from {t} WHERE rowid NOT IN '
                   '(SELECT MIN(rowid) FROM {t} GROUP BY timestamp, type)'.format(t=table))
    count = cur.fetchall()
    return count[0][0] if count else 0


def remove_duplicates(cursor, table):
    cursor.execute('DELETE FROM {t} WHERE rowid NOT IN '
                   '(SELECT MIN(rowid) FROM {t} GROUP BY timestamp, type)'.format(t=table))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check sensors in database of a node")
    parser.add_argument('db', help='Path to sqlite3 database file')
    parser.add_argument('-t', '--table', help='Table name', default='telemetry')
    parser.add_argument('-n', '--node', help='Node name', default=None)
    parser.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    assert os.path.exists(args.db)

    with sqlite3.connect(args.db) as con:
        cur = con.cursor()
        num_duped = count_duplicates(cur, args.table)
        print "Found {} duplicates".format(num_duped)

        if num_duped and args.remove:
            remove_duplicates(cur, args.table)
            con.commit()
            print "Found {} duplicates after removal".format(count_duplicates(con, args.table))
