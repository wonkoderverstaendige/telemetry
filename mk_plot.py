#!/usr/bin/env python

from Stopwatch import Stopwatch
startup = Stopwatch('Imports')
startup.start()
import pandas as pd
startup.event('pandas')
import matplotlib.pyplot as plt
startup.event('matplotlib')
import sqlite3
startup.event('sqlite3')
import subprocess
startup.event('subprocess')
# import time
# startup.event('time')
# import numpy as np
# startup.event('numpy')
# import logging
# startup.event('logging')
startup.report()

UPLOAD = True
SENSOR_HOST = 'chuck'
LOCAL_DB_PATH = 'db/telemetry.db'
LOCAL_IMG_PATH = 'plot.png'
REMOTE_IMG_PATH = '~/projects/static/'
REMOTE_HOST = 'lychnobite.me'


def read_df(from_id=0, **kwargs):
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch('Data frame loading')

    with sqlite3.connect(LOCAL_DB_PATH) as con:
        # TODO: Select only current host
        df = pd.read_sql_query('SELECT * FROM telemetry WHERE id>={id};'.format(id=from_id), con)
    sw.event('SQL raw data into df')

    return df, sw


def prepare_df(df, resample='5min', **kwargs):
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch('Data frame preparation')

    # timestamps as datetime array
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    sw.event('Timestamps to datetime')

    # type as category (sensor type)
    df['type'] = df['type'].astype('category')
    df['type'].cat.categories = [sensors_rev[c] for c in df['type'].cat.categories]
    sw.event('Type as category')

    # Pivot the table for fun and profit
    # NOTE: Will fail when duplicate entries (i.e. types must be unique per timestamp)
    df = df.pivot(index='timestamp', columns='type', values='value')
    sw.event('Pivot table')

    # Resample to given time interval
    if resample:
        df = df.resample(resample, how='mean')
        sw.event('Resampling to {}'.format(resample))

    # adjust time zone
    df = df.tz_localize('UTC').tz_convert('Europe/Amsterdam')
    sw.event('Timezone adjustment')

    return df, sw


def make_plot(df, plot_path=LOCAL_IMG_PATH, **kwargs):
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch('Plotting')
    
    p = df.plot()
    sw.event('Plotting of the df')

    fig = plt.gcf()
    fig.set_size_inches(20, 5)

    elapsed = sw.elapsed()
    p.annotate('{:.1f} s'.format(elapsed), xy=(1, 0), xycoords='axes fraction', fontsize=10, xytext=(0, -15),
               textcoords='offset points', ha='right', va='top')
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    sw.event('Saving figure')
    plt.close()
    plt.clf()

    return sw


def get_sensors(db_path, host):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM sensors WHERE host='{}';".format(host))
        return {s[2]: s[0] for s in cur.fetchall()}


def upload(img_path=LOCAL_IMG_PATH, dst=REMOTE_HOST):
    if UPLOAD:
        try:
            rc = subprocess.check_output(['scp', img_path, dst])
            print rc
        except subprocess.CalledProcessError, e:
            print "Failed to upload: {}".format(e)


if __name__ == "__main__":
    stopwatch = Stopwatch('Loading and plotting ALL THE DATA!')

    sensors = get_sensors(LOCAL_DB_PATH, SENSOR_HOST)
    sensors_rev = {v: k for k, v in sensors.iteritems()}

    data, stopwatch = read_df(resample='5min', sw=stopwatch)
    data, stopwatch = prepare_df(data, sw=stopwatch)

    make_plot(data, sw=stopwatch)
    upload(LOCAL_IMG_PATH, ":".join([REMOTE_HOST, REMOTE_IMG_PATH]))

    stopwatch.report()
