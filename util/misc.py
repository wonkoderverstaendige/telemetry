# -*- coding: utf-8 -*-

import os
import subprocess
import ConfigParser


def rev_dict(d):
    try:
        return {v: k for k, v in d.items()}
    except KeyError, error:
        print error


def upload(src, dst):
    try:
        return subprocess.check_output(['scp', src, dst])
    except subprocess.CalledProcessError, e:
        print "Failed to upload: {}".format(e)
        return {}


def get_local_config():
    """Return localhost.ini configuration as dictionary"""
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../config', 'localhost.ini'))
    cfg_dict = {s: dict(config.items(s)) for s in config.sections()}

    # make the relative paths into a universally useful absolute paths
    for name, path in cfg_dict['paths'].items():
        cfg_dict['paths'][name] = os.path.abspath(path)

    return cfg_dict
