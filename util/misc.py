# -*- coding: utf-8 -*-

import os
import subprocess
import ConfigParser
import time
from datetime import datetime as dt


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


def timestamp():
    t = dt.now()
    return time.mktime(t.timetuple())+(t.microsecond/1e6)


def iso_date(ts=None):
    """Return iso date (year, week number, day of week) of timestamp.
    If no timestamp or date was given, uses datetime.now()

    Uses the ISO 8601 definition of "week":
        A week starts on Monday
        A week has to have at least 4 days in a year to count in that year
        There are 51..53 weeks
        Starts at week 1
        :param ts: Timestamp or date. Default: None->datetime.now()
    """
    return dt.isocalendar(ts if ts else dt.now())


def iso_year(*args, **kwargs):
    return iso_date(*args, **kwargs)[0]


def iso_week(*args, **kwargs):
    return iso_date(*args, **kwargs)[1]


def iso_to_gregorian(iso_year, iso_week, iso_day):
    """Gregorian calendar date for the given ISO year, week and day

    From: http://stackoverflow.com/a/33101215"""
    fifth_jan = dt.date(iso_year, 1, 5)
    _, fifth_jan_week, fifth_jan_day = fifth_jan.isocalendar()
    return fifth_jan + dt.timedelta(days=iso_day-fifth_jan_day, weeks=iso_week-fifth_jan_week)