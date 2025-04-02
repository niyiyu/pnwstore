import pandas as pd
import os
import glob
from tqdm import tqdm
import socket

from .constants import wd_mapper, sqlite_mapper

def wildcard_mapper(c):
    if "*" in c:
        c = c.replace("*", "%")
    if "?" in c:
        c = c.replace("?", "_")
    return c


def pnwstore_filename_mapper(filename):
    year = int(filename.split("/")[5])
    return "/auto/pnwstore1-" + wd_mapper[year] + filename[10:]


def dummy_filename_mapper(filename):
    return filename


def sqlite_base():
    return sqlite_mapper[socket.gethostname()]


def dbs_mapper(year):
    sqlite_path = sqlite_base()
    return sqlite_path + "%d.sqlite" % year


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
