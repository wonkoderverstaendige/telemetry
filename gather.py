#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import socket
from util.misc import get_local_config, iso_date, iso_week

LOCAL_CONFIG = get_local_config()
SENSOR_HOST = LOCAL_CONFIG['host']['node']

LOCAL_HOST_NAME = socket.gethostname()
LOCAL_NODE_NAME = LOCAL_CONFIG['host']['node']
assert LOCAL_HOST_NAME == LOCAL_CONFIG['host']['name']

LOCAL_DB_PATH = LOCAL_CONFIG['paths']['db']


DTYPE_VAL = np.float32
DTYPE_CAT = np.uint8
nodes = {'chuck': 0, 'bed': 1}
sensors = {0: {'temp': 1, 'light': 2, 'soil':3, 'dummy': 4, 'ds_temp':5},
           1: {'strain': 6, 'temp': 7, 'motion': 8}}
# needed because of the naming overlap in the sensors. [b/c]x are placeholders for debugging.
cats = {0: ['c0', 'temp', 'light', 'soil', 'c4', 'ds_temp', 'c6',  'c7'],
        1: ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'strain',  'temp',  'motion']}


def nid_from_filename(file_path):
    return nodes[os.path.basename(file_path).split('-')[-1].split('.')[0]]


def load_node_csv(file_path, nid=None):
    nid = nid if nid is not None else nid_from_filename(file_path)
    data = pd.read_csv(file_path, names=['timestamp', 'sensor_str', 'value'], skiprows=1,
                       dtype={'timestamp': np.float64, 'sensor_str': str, 'value': DTYPE_VAL})
    data.set_index(data.timestamp.multiply(1e9).astype('datetime64[ns]'), inplace=True)

    sid = data.sensor_str.astype('category', categories=cats[nid_from_filename(file_path)]).cat.codes.astype(DTYPE_CAT)
    return pd.DataFrame({'sid': sid, 'nid': np.array(nid, dtype=np.uint8), 'value': data.value})


def load_hdf(hdf_file_path):
    return pd.read_hdf(hdf_file_path, 'data')


def last_samples_hdf(df):
    df.sort_index(inplace=True)
    assert df.index.is_monotonic
    g = df.groupby('nid')
    return {k: g.get_group(k).index[-1] for k in [0, 1]}


if __name__ == "__main__":
    OFFSET = 2
    sources = [{'host': 'VersedSquid', 'node': 'chuck', 'src': '~/code/telemetry/local/db/',
                'iso': iso_date(), 'dst': LOCAL_DB_PATH},
               {'host': 'RandyDolphin', 'node': 'bed', 'src': '~/code/telemetry/local/db/',
                'iso': iso_date(), 'dst': LOCAL_DB_PATH}]
    if iso_week(offset=0) != iso_week(offset=OFFSET):
        import copy
        print "Updating last weeks data, too"
        sources.extend(copy.deepcopy(sources))
        for n in range(len(sources) / 2):
            sources[n]['iso'] = iso_date(offset=OFFSET)

    for src in sources:
        if src['host'] == LOCAL_HOST_NAME:
            print "Skipping localhost"
            continue
        os.system("rsync -avh {host}:{src}{iso[0]:}_w{iso[1]:02}-{node}.csv {dst}".format(**src))

    last = last_samples_hdf(load_hdf(os.path.join(LOCAL_DB_PATH, 'telemetry.h5')))
    node_data = [load_node_csv(os.path.join(LOCAL_DB_PATH, '{iso[0]:}_w{iso[1]:02}-{node}.csv'.format(**src)))
                 for src in sources]
    df = pd.concat([node_data[n][node_data[n].index > last[n]] for n in range(len(node_data))]).sort_index()

    # FIXME: For some reason the values column is _sometimes_ cast to float64! The hell?
    df.value = df.value.astype(np.float32)

    try:
        if df.shape[0]:
            print df.shape[0], "new rows to be appended!"
            with pd.HDFStore(os.path.join(LOCAL_DB_PATH, 'telemetry.h5')) as store:
                store.append('data', df, append=True)
        else:
            print "Nothing new."
    except ValueError, error:
        print error
        print df.dtypes
