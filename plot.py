#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Stopwatch import Stopwatch
startup = Stopwatch('Imports')
startup.start()
import os
startup.event('os')
import pandas as pd
startup.event('pandas')
import matplotlib.pyplot as plt
startup.event('matplotlib')
import sqlite3
startup.event('sqlite3')
import subprocess
startup.event('subprocess')
import socket
startup.event('socket')
from datetime import datetime
startup.event('datetime.datetime')
# import time
# startup.event('time')
# import numpy as np
# startup.event('numpy')
# import logging
# startup.event('logging')
startup.report()

PATH = os.path.dirname(os.path.realpath(__file__))
INDEX_START = 0
UPLOAD = True
SENSOR_HOST = 'chuck'
LOCAL_HOSTNAME = socket.gethostname()
LOCAL_DB_PATH = os.path.join(PATH, 'db/telemetry.db')
assert(os.path.exists(LOCAL_DB_PATH))
LOCAL_IMG_PATH = os.path.join(PATH, 'var/plot.png')

REMOTE_IMG_PATH = '~/srv/www/static/'
REMOTE_HOST = 'lychnobite.me'
PLOT_WIDTH_PER_DAY = .8
PLOT_HEIGHT = 5.0


def read_df(from_id=0, **kwargs):
    # TODO: Select only current host
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch('Data frame loading')

    with sqlite3.connect(LOCAL_DB_PATH) as con:
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


def make_plot(df, plot_path, **kwargs):
    sw = kwargs['sw'] if 'sw' in kwargs else Stopwatch('Plotting')

    # Throw all the data into a plot, temperature as a secondary scale
    axes = df.plot(secondary_y='temp', mark_right=False, style=['red', 'black', 'blue'])
    sw.event('Plotting of the df')

    fig = plt.gcf()
    # Adjust plot width by number of days shown
    delta = (df.index[-1] - df.index[0]) / pd.Timedelta('1 Day')
    fig.set_size_inches(delta*PLOT_WIDTH_PER_DAY, PLOT_HEIGHT)
    fig.tight_layout()

    # Fiddling with axis labeling
    # plt.xticks([])
    axes.set_ylabel(u'Arbitrary ADC values')
    axes.right_ax.set_ylabel(u'Temperature (°C)')
    axes.set_yticks([])  # no labels on the arbitrary ADC range
    axes.set_xlabel('')

    # Messing with the legend, correcting order of paining (or first legend is behind axes)
    left_legend = axes.legend(loc='upper left', shadow=True, fontsize='medium')
    #axes.legend = None
    #axes.right_ax.add_artist(left_legend)
    axes.right_ax.legend(loc='upper right', shadow=True, fontsize='medium')

    # Annotation to show date of creation and file origin
    elapsed = sw.elapsed()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    axes.annotate('{elapsed:.1f} s on {hostname}, {timestamp}'
                  .format(elapsed=elapsed,
                          hostname=LOCAL_HOSTNAME,
                          timestamp=now),
                  xy=(1, 0), xycoords='axes fraction', fontsize=10, xytext=(0, -55),
                  textcoords='offset points', ha='right', va='top')
    sw.event('Plot annotation')

    sw.event('Saving figure')
    fig.savefig(plot_path, transparent=False, bbox_inches='tight', pad_inches=0)

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

    data, stopwatch = read_df(INDEX_START, resample='5min', sw=stopwatch)
    data, stopwatch = prepare_df(data, sw=stopwatch)

    make_plot(data, plot_path=LOCAL_IMG_PATH, sw=stopwatch)
    upload(LOCAL_IMG_PATH, ":".join([REMOTE_HOST, REMOTE_IMG_PATH]))

    stopwatch.report()
