#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.Stopwatch import Stopwatch
# startup = Stopwatch('Imports')
# startup.start()
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import socket
import numpy as np
from util import db_io
from util.misc import get_local_config
import sqlite3
# startup.report()

LOCAL_CONFIG = get_local_config()
SENSOR_HOST = LOCAL_CONFIG['host']['node']

LOCAL_HOST_NAME = socket.gethostname()
LOCAL_NODE_NAME = LOCAL_CONFIG['host']['node']
assert LOCAL_HOST_NAME == LOCAL_CONFIG['host']['name']

LOCAL_DB_PATH = LOCAL_CONFIG['paths']['db']

LOCAL_VAR_PATH = LOCAL_CONFIG['paths']['var']
assert(os.path.exists(LOCAL_VAR_PATH)), LOCAL_VAR_PATH

REMOTE_VAR_PATH = '~/srv/www/static/'
REMOTE_HOST = 'lychnobite.me'

INDEX_START = 0
PLOT_WIDTH_PER_DAY = .8
PLOT_HEIGHT = 9.0


def make_plot(df, plot_path, **kwargs):
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)

    # Adjust plot width by number of days shown
    delta = (df.index[-1] - df.index[0]) / pd.Timedelta('1 Day')
    fig.set_size_inches(delta*PLOT_WIDTH_PER_DAY, PLOT_HEIGHT)
    fig.tight_layout()

    groups = df.groupby(['type'], sort=False)
    axes = list(axes)
    axes_bed = [axes[0], axes[0].twinx()]
    axes_chuck = [axes[1], axes[1].twinx()]

    sensors = kwargs['sensors'] if 'sensors' in kwargs else range(10)

    pd.plot_params.use('x_compat', True)

    # digital temp chuck
    groups.get_group(5).value.resample('6min').plot(ax=axes_chuck[1], style='c', label="d_temp")
    # soil
    groups.get_group(3).value.resample('6min').plot(ax=axes_chuck[0], style='b', label="soil")
    # light
    groups.get_group(2).value.resample('6min').plot(ax=axes_chuck[0], style='g', label="light")
    # a_temp
    groups.get_group(1).value.resample('6min').plot(ax=axes_chuck[0], style='g', label="a_temp")

    date_range = axes_chuck[1].get_xlim()

    groups.get_group(7).value.resample('6min').plot(ax=axes_bed[0], style='k', label='strain')
    groups.get_group(8).value.resample('6min').plot(ax=axes_bed[1], style='r', label='d_temp')

    # Left side
    for a in [axes_bed[0], axes_chuck[0]]:
        a.set_ylabel(u'Arbitrary ADC values')
        a.set_yticks([])  # no labels on the arbitrary ADC range
        a.set_ylim((0, 1023))
        a.set_xlabel('')

    # Right side
    for a in [axes_bed[1], axes_chuck[1]]:
        a.legend(loc='upper right', shadow=True, fontsize='medium')
        a.set_ylim((10, 40))
        a.set_ylabel(u'Temperature (°C)')
        # Messing with the legend, correcting order of painting (or first legend is behind axes)
        a.legend(loc='upper left', shadow=True, fontsize='medium')

    axes_chuck[0].set_xlim(date_range)

    fig.savefig(os.path.join(plot_path, 'plot.png'),
                transparent=False, bbox_inches='tight', pad_inches=0)


if __name__ == "__main__":
    # TODO: Move some of the constants into command line stuff with defaults
    parser = argparse.ArgumentParser(description="Make pretty plot of telemetry data")
    parser.add_argument('-db', help='Path to sqlite3 database file',
                        default=os.path.join(LOCAL_DB_PATH, 'telemetry.db'))
    parser.add_argument('-n', '--node', help='Node name (e.g. restrict to plotting "chuck"')
    parser.add_argument('-u', '--upload', help='Upload results to web server')
    cli_args = parser.parse_args()

    assert(os.path.exists(cli_args.db)), cli_args.db

    with sqlite3.connect(cli_args.db) as con:
        cursor = con.cursor()
        sensors = db_io.sql_sensor_description(cursor, host=LOCAL_NODE_NAME)
        data = db_io.sql_table2df(con, 'telemetry')

    data = db_io.prepare_df(data)

    # Load old bed data
    old = pd.read_csv(os.path.join(LOCAL_DB_PATH, 'markII.csv'), names=['timestamp', 'wmin', 'wmax'])
    old.timestamp = old.timestamp.astype('datetime64[s]')
    old.set_index('timestamp', inplace=True)
    old = old.tz_localize('UTC').tz_convert('Europe/Amsterdam')
    old = pd.concat([pd.DataFrame({'type': 6, 'value': old.wmax}),
                     pd.DataFrame({'type': 7, 'value': old.wmax})])

    # Append the new bed data
    bed = db_io.prepare_df(db_io.csv_table2df(os.path.join(LOCAL_DB_PATH, 'bed.csv')))
    bed = pd.concat([old, bed])
    data = pd.concat([data, bed])

    make_plot(data, LOCAL_VAR_PATH)

    #misc.upload_scp(LOCAL_VAR_PATH, ":".join([REMOTE_HOST, REMOTE_VAR_PATH]))
