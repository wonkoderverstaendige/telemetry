#!/usr/bin/env python

from Stopwatch import Stopwatch
startup = Stopwatch('Imports')
startup.start()
import time
startup.event('time')
import pandas as pd
startup.event('pandas')
import matplotlib.pyplot as plt
startup.event('matplotlib')
import sqlite3
startup.event('sqlite3')
import numpy as np
startup.event('numpy')
import subprocess
startup.event('subprocess')
import logging
startup.event('logging')
startup.report()

LOOP = 0
UPLOAD = True
HOST = 'chuck'
DB_PATH = '/home/reichler/telemetry.db'
IMG_OUT = 'plot.png'

def read_df(db_path, host, resample=False, from_id=0, sw=None):
    # TODO: Select only current host
    if sw is None:
        sw = Stopwatch('Dataframe loading and processing')

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute('SELECT MAX(id) FROM telemetry;')
        last_id = cur.fetchone()[0]
        
        # if we didn't get anything from that query, return current id
        # may have new data later...
        if from_id > last_id:
            return None, from_id, sw
        
        df = pd.read_sql_query('SELECT * FROM telemetry where id>={} AND id<={};'.format(from_id, last_id), con)
    sw.event('SQL raw data into df')

    # timestamps as datetime array
    #df.set_index('timestamp')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    sw.event('convert timestamps to datetime')
    
    # type as category (sensor type)
    df['type'] = df['type'].astype('category')
    newcats = [sensors_rev[c] for c in df['type'].cat.categories]
    df['type'].cat.categories = newcats
    sw.event('type as category')
  
    pivoted = df.pivot(index = 'timestamp', columns='type', values='value')
    sw.event('pivot table')
    
    if resample:
        pivoted = pivoted.resample(resample, how='mean')
        sw.event('resampling')

    # make temperature more visible # hack, hack
    pivoted['temp'] *=10
    sw.event('scale temperature')

    # adjust time zone
    pivoted = pivoted.tz_localize('UTC').tz_convert('Europe/Amsterdam')
    sw.event('adjust timezone')
    
    return pivoted, last_id, sw


def make_plot(df, plot_path, sw=None):
    if sw is None:
        sw = Stopwatch('Plotting')
    
    p = df.plot()
    sw.event('plot')

    fig = plt.gcf()
    fig.set_size_inches(20, 5)

    elapsed = sw.elapsed()
    p.annotate('{:.0f} s'.format(elapsed), xy=(1, 0), xycoords='axes fraction', fontsize=10, xytext=(0, -15),
                              textcoords='offset points', ha='right', va='top')
    fig.tight_layout()
    fig.savefig(plot_path, dpi=150)
    sw.event('savefig')
    plt.close()
    plt.clf()
    sw.event('close plt')
    
    return sw

def get_sensors(db_path, host):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM sensors WHERE host='{}';".format(host))
        sensors = {s[2]: s[0] for s in cur.fetchall()}
    return sensors


if __name__ == "__main__":
    sensors = get_sensors(DB_PATH, HOST)
    sensors_rev = {v:k for k, v in sensors.iteritems()}
    
    last_id = 0
    telemetry = None
    
    while True:
        print "read from ", last_id
        fragment, ret_id, sw = read_df(DB_PATH, HOST, resample='5min', from_id=last_id)
        print 'read until', ret_id
        if fragment is not None:
            last_id = ret_id + 1
            if telemetry is None:
                telemetry = fragment
            else:
                print "Adding {} lines.".format(len(fragment))
                telemetry.append(fragment)
            make_plot(telemetry, IMG_OUT, sw)
            if UPLOAD:
                try:
                    rc = subprocess.check_output(['scp', 'plot.png', 'lychnobite.me:~/projects/static/'])
                    print rc
                except subprocess.Error, e:
                    print "Failed to upload: {}".format(e)

        sw.report()
        time.sleep(LOOP)

        sw = None
        if not LOOP:
            break
