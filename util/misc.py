# -*- coding: utf-8 -*-

import os
import subprocess
import ConfigParser


def rev_dict(d):
    try:
        return {v: k for k, v in d.items()}
    except KeyError, error:
        print error


def upload_scp(src, dst):
    """
    Upload src file to dst via scp
    :param src:
    :param dst:
    :return: None if failed, else return code
    """
    try:
        return subprocess.check_output(['scp', src, dst])
    except subprocess.CalledProcessError, error:
        print "Failed to upload: {}".format(error)
        return error


def get_local_config():
    """
    Grab config as dictionary.
    :return: dict() of local configuration
    """
    this_file = os.path.dirname(__file__)
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(this_file, '../config', 'localhost.ini'))
    cfg_dict = {s: dict(config.items(s)) for s in config.sections()}

    # make the relative paths into a universally useful absolute paths
    for name, path in cfg_dict['paths'].items():
        cfg_dict['paths'][name] = os.path.abspath(os.path.join(this_file, path))
    return cfg_dict
