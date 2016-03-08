import os
import sqlite3

def density(filename, table):
    with sqlite3.connect(filename) as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM {};".format(table))
        rows = int(cur.fetchone()[0])
        size = os.path.getsize(filename)
        return rows, size, 1.0*size/rows

filenames = {'telemetry.db':'telemetry',
             'telemetry_shorter_timestamps.db':'Chuck',
             'telemetry_string_date.db':'Chuck'}
for filename, table in filenames.iteritems():
    filler = " "*(max(map(len, filenames))-len(filename))
    rows, size, ratio = density(filename, table)
    ps = ratio*3/5
    pa = ps * 60 * 60 * 24 * 365 / 1e6
    print "{}{}: {} rows, {:.1f}KB, {:.1f} B/row, {:.1f}B/s, {:.1f}MB/yr".format(filename, filler, rows, size/1e3, ratio, ps, pa)

