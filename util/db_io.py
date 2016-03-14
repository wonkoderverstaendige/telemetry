# -*- coding: utf-8 -*-

import argparse
import sqlite3
import subprocess

import numpy
import pandas

import Stopwatch
from misc import get_local_config


def sql_table2df(db, table, from_id=0, **kwargs):
    # TODO: Select only current host
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch.Stopwatch('Data frame loading')

    with sqlite3.connect(db) as con:
        df = pandas.read_sql_query('SELECT * FROM {t} WHERE id>={id}'.format(t=table, id=from_id), con)
    sw.event('SQL raw data into df')

    return df, sw


def prepare_df(df, sensors, resample='5min', **kwargs):
    sensors = sql_sensor_description()
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch.Stopwatch('Data frame preparation')

    # timestamps as datetime array
    df['timestamp'] = pandas.to_datetime(df['timestamp'], unit='s')
    sw.event('Timestamps to datetime')

    # TODO: Translate category elsewhere?
    # type as category (sensor type)
    # df['type'] = df['type'].astype('category')
    # df['type'].cat.categories = [sensors_rev[c] for c in df['type'].cat.categories]
    # sw.event('Type as category')

    # Pivot the table for fun and profit
    # NOTE: Will fail when duplicate entries (i.e. types must be unique per timestamp)
    df = df.pivot(index='timestamp', columns='type', values='value')
    sw.event('Pivot table')

    # Resample to given time interval
    if resample:
        df = df.resample(resample, how='mean')
        sw.event('Resampling to {}'.format(resample))

    df.temp[(df['light'] > 250) & (df.index < '2016-03-10 07:03:57.603722+01:00')] = numpy.NaN
    sw.event("Remove false temp values.")

    # adjust time zone
    df = df.tz_localize('UTC').tz_convert('Europe/Amsterdam')
    sw.event('Timezone adjustment')

    return df, sw


# def sql_sensor_ids(cursor, host=None, table='sensors'):
#     """
#     Get the name and ids of sensors in the db of the cursor.
#     :param cursor: sqlite3 db cursor.
#     :param host: Restrict selection to sensors belonging to host/node.
#     :param table: Name of table containing sensor descriptions. (default='sensors')
#     :return: Dictionary of {sensorID: sensorName}
#     """
#     try:
#         condition = "WHERE host='{}'".format(host) if host else ''
#         cursor.execute("SELECT * FROM {}".format(table) + condition)
#         return {s[0]: s[2] for s in cur.fetchall()}
#     except sqlite3.Error, e:
#         print "Error: {}".format(e)


def sql_sensor_description(cursor, host=None, table='sensors'):
    """
    Get the description for sensors.
    :param cursor: sqlite3 db cursor.
    :param host: Restrict selection to sensors belonging to host/node.
    :param table: Name of table containing sensor descriptions. (default='sensors')
    :return: Dictionary of {sensorID: (host, factor, unit, description)}
    """
    try:
        query = "SELECT * FROM {} ".format(table) + 'WHERE host="{}"'.format(host) if host else ''
        cursor.execute(query)
        return {s[0]: (s[1], s[2], s[3], s[4], s[5]) for s in cursor.fetchall()}
    except sqlite3.Error, e:
        print "Error: {}".format(e)


def sql_duplicates_count(cursor, table='telemetry'):
    """
    Check table for duplicate entries.
    :param cursor: sqlite3 db cursor
    :param table: name of table to check
    :return: Number of duplicate rows found. 0 if none.
    """
    cursor.execute('SELECT COUNT(*) from {t} WHERE rowid NOT IN '
                   '(SELECT MIN(rowid) FROM {t} GROUP BY timestamp, type)'.format(t=table))
    count = cur.fetchall()
    assert count, "Counting duplicates failed: {}".format(str(count))
    return count[0][0]


def sql_duplicates_remove(cursor, table='telemetry'):
    """
    Remove duplicate rows in the given db table
    :param cursor: sqlite3 db cursor
    :param table: name of table to remove duplicates from
    :return: None
    """
    cursor.execute('DELETE FROM {t} WHERE rowid NOT IN '
                   '(SELECT MIN(rowid) FROM {t} GROUP BY timestamp, type)'.format(t=table))


def sql_check_consistency(cursor):
    """
    Checks for file consistency. Things can and will get corrupted, often by copying
    while the file is being written into by another process. This seems to be hard to
    recover from. Sooo... MAKE BACKUPS!

    :param cursor: sqlite3 db cursor
    :return: Status of db. Either "ok" or some error message, likely corrupted file.
    """
    return cursor.execute('pragma integrity_check').fetchone()[0]


def sql_check_db(*args, **kwargs):
    """
    General check of db state.

    Currently  and number of duplicate rows in sensor data table.

    :param args: Cursor to db
    :param kwargs: Name of database table.
    :return: Number of duplicate rows found, (0 if none) and None if assertion fails.
    """
    consistency = sql_check_consistency(*args)
    assert consistency == u'ok', "DB consistency check failed: {}".format(consistency)
    num_duplicates = sql_duplicates_count(*args)
    assert num_duplicates == 0, "{} duplicate entries detected!".format(num_duplicates)
    return num_duplicates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check sensors in database of a node")
    parser.add_argument('-db', help='Path to sqlite3 database file')
    parser.add_argument('-n', '--node', help='Node name')
    cli_args = parser.parse_args()

    config = get_local_config()
    db = cli_args.db if cli_args.db else config['paths']['db']
    node = cli_args.node if cli_args.node else config['host']['node']

    with sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()
        assert sql_check_db(cur) is 0
        print "Id\t host\t type\t f*unit\t description"
        print "-------------"
        for k, v in sql_sensor_description(cur, node).items():
            host, name, description, factor, unit = v

            print '{}\t{}\t{}\t{} {}\t{}' \
                  .format(k, name, host, factor, unit.encode('utf-8'), description)
