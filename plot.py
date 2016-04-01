#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')

import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mpl_lines
from util.misc import get_local_config, upload_scp

LOCAL_CONFIG = get_local_config()
SENSOR_HOST = LOCAL_CONFIG['host']['node']
LOCAL_HOST_NAME = LOCAL_CONFIG['host']['name']
LOCAL_NODE_NAME = LOCAL_CONFIG['host']['node']

LOCAL_DB_PATH = LOCAL_CONFIG['paths']['db']
assert(os.path.exists(LOCAL_CONFIG['paths']['db']))
LOCAL_VAR_PATH = LOCAL_CONFIG['paths']['var']
assert(os.path.exists(LOCAL_VAR_PATH)), LOCAL_VAR_PATH

PLOT_WIDTH_PER_DAY = 1.5
PLOT_HEIGHT = 8

RESAMPLE = '6min'

REMOTE_VAR_PATH = '~/srv/www/static/plot.png'
REMOTE_HOST = 'lychnobite.me'

CHUCK = 0
BED = 1
nodes = {'chuck': CHUCK, 'bed': BED}
sensors = {0: {'temp': 1, 'light': 2, 'soil': 3, 'dummy': 4, 'ds_temp':5},
           1: {'strain': 6, 'temp': 7, 'motion': 8}}
# needed because of the naming overlap in the sensors. [b/c]x are placeholders for debugging.
cats = {0: ['c0', 'temp', 'light', 'soil', 'c4', 'ds_temp', 'c6',  'c7'],
        1: ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'strain',  'temp',  'motion']}


def spans(df):
    assert df.index.is_monotonic
    drs = pd.date_range(df.index[0].normalize(), df.index[-1].normalize(), freq='D')
    return zip(drs, drs + pd.DateOffset(hour=8))


def plot(df):
    # FIXME: Something is up with appending...
    df.sort_index(inplace=True)
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
    delta = (df.index[-1] - df.index[0]) / pd.Timedelta('1 Day')
    fig.set_size_inches(delta*PLOT_WIDTH_PER_DAY, PLOT_HEIGHT)
    fig.tight_layout()
    # pd.plot_params.use('x_compat', False)

    axes = list(ax)
    axes_bed = [axes[0], axes[0].twinx()]
    axes_chuck = [axes[1], axes[1].twinx()]

    groups = df.groupby(['sid'])

    # BED: strain, motion & temp
    groups.get_group(sensors[BED]['strain']).value.resample(RESAMPLE).mean().plot(ax=axes_bed[0], style='k', label=r'$m_{strain}$')
    axes_bed[0].eventplot(groups.get_group(sensors[BED]['motion']).value.index,
                          linewidths=.2, colors='b', linelengths=30, lineoffsets=700)
    ep_artist = mpl_lines.Line2D([], [], color='b', label=r'motion')
    groups.get_group(sensors[BED]['temp']).value.resample(RESAMPLE).mean().plot(ax=axes_bed[1], style='r', label=r'$T_{bedroom}$')

    # CHUCK: soil, light, temp, ds_temp
    groups.get_group(sensors[CHUCK]['ds_temp']).value.resample(RESAMPLE).mean().plot(ax=axes_chuck[1], style='r', label=r'$T_{desk}$')
    groups.get_group(sensors[CHUCK]['light']).value.resample(RESAMPLE).mean().plot(ax=axes_chuck[0], style='g', label="$lum_{chuck}$")
    groups.get_group(sensors[CHUCK]['soil']).value.resample(RESAMPLE).mean().bfill().plot(ax=axes_chuck[0], style='b', label=r"$moisture_{soil}$")
    # groups.get_group(1).value.resample('6min').plot(ax=axes_chuck[1], style='r', label="a_temp")

    # Legend bed
    handles, labels = axes_bed[0].get_legend_handles_labels()
    handles.append(ep_artist)
    handles_r, labels_r = axes_bed[1].get_legend_handles_labels()
    legend_r = axes_bed[1].legend(handles=handles_r, loc='upper right', shadow=True, fontsize='medium')
    axes_bed[1].add_artist(legend_r)
    axes_bed[1].legend(handles=handles, title='[Bed]', loc='upper left', shadow=True, fontsize='medium')

    # Legend chuck
    handles, labels = axes_chuck[0].get_legend_handles_labels()
    handles_r, labels_r = axes_chuck[1].get_legend_handles_labels()
    legend_r = axes_chuck[1].legend(handles=handles_r, loc='upper right', shadow=True, fontsize='medium')
    axes_chuck[1].add_artist(legend_r)
    axes_chuck[1].legend(handles=handles, title='[Chuck]', loc='upper left', shadow=True, fontsize='medium')

    # Left side
    axes_chuck[0].set_ylim((0, 1023))
    for a in [axes_chuck[0], axes_bed[0]]:
        a.set_ylabel(u'Arbitrary ADC values')
        a.set_yticks([])  # no labels on the arbitrary ADC range
    axes_bed[0].set_ylim((500, 800))
    #axes_bed[0].set_xticks([])
    #axes_bed[1].set_xticks([])
    #axes_chuck[0].set_xlabel('')

    # shade 0-8 am
    for span in spans(df):
        axes_chuck[1].axvspan(span[0], span[1], facecolor='0.2', alpha=0.1)
        axes_bed[1].axvspan(span[0], span[1], facecolor='0.2', alpha=0.1)

    # Right side
    for a in [axes_bed[1], axes_chuck[1]]:
        a.set_ylim((15, 35))
        a.set_ylabel(u'Temperature (°C)')

    axes_chuck[0].annotate('{hostname}, {timestamp}'
                           .format(hostname=LOCAL_HOST_NAME,
                                   timestamp=pd.Timestamp.now(),),
                           xy=(1, 0), xycoords='axes fraction', fontsize=10, xytext=(0, -55),
                           textcoords='offset points', ha='right', va='top')

    # Save to file
    fig.savefig(os.path.join(LOCAL_VAR_PATH, 'plot_chuck_bed.png'),
                transparent=False, bbox_inches='tight', pad_inches=.1)


if __name__ == "__main__":
    # TODO: Move some of the constants into command line stuff with defaults
    parser = argparse.ArgumentParser(description="Make pretty plot of telemetry data")
    parser.add_argument('-db', help='Path to hdf5 file.',
                        default=os.path.join(LOCAL_DB_PATH, 'telemetry.h5'))
    parser.add_argument('-u', '--upload', action='store_true', help='Upload results to web server')
    cli_args = parser.parse_args()

    assert(os.path.exists(cli_args.db))
    data = pd.read_hdf(cli_args.db, 'data').tz_localize('UTC').tz_convert('Europe/Amsterdam')
    plot(data)

    # if cli_args.upload:
    #     upload_scp(os.path.join(LOCAL_VAR_PATH, 'plot_chuck_bed.png'), ":".join([REMOTE_HOST, REMOTE_VAR_PATH]))
