# -*- coding: utf-8 -*-

import argparse
import sqlite3

import pandas

from misc import get_local_config


def csv_table2df(csv_file):
    df = pandas.read_csv(csv_file, names=['timestamp', 'type', 'value'])
    df.type.loc[df.type == 'strain_lo'] = 6
    df.type.loc[df.type == 'strain_hi'] = 7
    df.type.loc[df.type == 'temp'] = 8
    df.type.astype('uint8')
    return df


def sql_table2df(sql_con, table, start=0, end=None, **kwargs):
    """
    Read table from connection into a pandas data frame.
    :param sql_con: sqlite3 connection object. NOTE: Not cursor!
    :param table: table to read from
    :param start: Start, in unix epoch time, default = 0
    :param end: End, in unix epoch time, default = None
    :param kwargs: **kwargs
    :return:
    """
    # TODO: Select only current host
    query = 'SELECT timestamp, type, value FROM {table}'.format(table=table)
    if end is not None:
        assert start < end, "End ({}) must be larger then start ({})".format(end, start)
    if start or end:
        condition = 'rowid>{}'.format(start) if start else ''
        condition += ' AND ' if start and end else ''
        condition += 'rowid<{}'.format(end) if end else ''
        query += ' WHERE({:s})'.format(condition)
    return pandas.read_sql_query(query, sql_con)


def prepare_df(df):
    df.timestamp = df.timestamp.astype("datetime64[s]")
    df.set_index('timestamp', inplace=True)
    df.tz_localize('UTC', copy=False) \
      .tz_convert('Europe/Amsterdam', copy=False)

    # TODO: Translate category elsewhere?
    # type as category (sensor type)
    # df['type'] = df['type'].astype('category')
    # df['type'].cat.categories = [sensors_rev[c] for c in df['type'].cat.categories]

    # Pivot the table for fun and profit
    # NOTE: Will fail when duplicate entries (i.e. types must be unique per timestamp)
    # df = df.pivot(index='timestamp', columns='type', values='value')

    # Resample to given time interval
    # if resample:
    #     df = df.resample(resample, how='mean')
    # df.temp[(df['light'] > 250) & (df.index < '2016-03-10 07:03:57.603722+01:00')] = numpy.NaN
    return df


def sql_sensor_description(cursor, host=None, table='sensors'):
    """
    Get the description for sensors.
    :param cursor: sqlite3 db cursor.
    :param host: Restrict selection to sensors belonging to host/node.
    :param table: Name of table containing sensor descriptions. (default='sensors')
    :return: Dictionary of {sensorID: (host, factor, unit, description)}
    """
    try:
        query = "SELECT * FROM {} ".format(table) + ('WHERE host="{}"'.format(host) if host else '')
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
    consistency = sql_check_consistency(*args, **kwargs)
    assert consistency == u'ok', "DB consistency check failed: {}".format(consistency)
    num_duplicates = sql_duplicates_count(*args, **kwargs)
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

    with sqlite3.connect(db) as con:
        cur = con.cursor()
        assert sql_check_db(cur) is 0
        print "Id\t host\t type\t f*unit\t description"
        print "-------------"
        for k, v in sql_sensor_description(cur, node).items():
            host, name, description, factor, unit = v

            print '{}\t{}\t{}\t{} {}\t{}' \
                  .format(k, name, host, factor, unit.encode('utf-8'), description)
