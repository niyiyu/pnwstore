import pandas as pd
import os
import glob
from tqdm import tqdm


def year2day(quake_year):
    if quake_year == 2010:
        return 8
    elif quake_year == 2017:
        return 7
    elif quake_year == 2022:
        return 3
    else:
        return abs(quake_year - 2031) % 11


def wildcard_mapper(c):
    if "*" in c:
        c = c.replace("*", "%")
    if "?" in c:
        c = c.replace("?", "_")
    return c


def pnwstore_filename_mapper(filename):
    return "/auto/pnwstore1-" + filename[6:]


def dummy_filename_mapper(filename):
    return filename


def sqlite_base():
    import socket

    sqlite_mapper = {
        "cascadia.ess.washington.edu": "/data/wsd01/PNWstore_sqlite/",
        "siletzia.ess.washington.edu": "/fd1/yiyu_data/PNWstore_sqlite/",
        "marine1.ess.washington.edu": "/mnt/DATA0/PNWstore_sqlite/",
        "psf-nvme01-prd-j375.ess.washington.edu": "/wd1/PNWstore_sqlite/"
    }
    return sqlite_mapper[socket.gethostname()]


def dbs_mapper(year):
    sqlite_path = sqlite_base()
    return sqlite_path + "%d.sqlite" % year


def mseedkeys():
    return [
        "network",
        "station",
        "location",
        "channel",
        "quality",
        "version",
        "starttime",
        "endtime",
        "samplerate",
        "filename",
        "byteoffset",
        "bytes",
        "hash",
        "timeindex",
        "timespans",
        "timerates",
        "format",
        "filemodtime",
        "updated",
        "scanned",
    ]


def rst2df(result, keys=None):
    if isinstance(keys, str):
        return pd.DataFrame(result, columns=[keys])
    elif isinstance(keys, list):
        return pd.DataFrame(result, columns=keys)
    else:
        return pd.DataFrame(result)


def index_folder(path, sqlite_path, mseedindex_cmd="mseedindex"):
    leap_env = "LIBMSEED_LEAPSECOND_FILE=../leap-seconds.list"
    for i in tqdm(glob.glob(path + "/**/*", recursive=True)):
        if not os.path.isdir(i):
            cmd = " ".join([leap_env, mseedindex_cmd, i, "-sqlite", sqlite_path])
            os.system(cmd)
