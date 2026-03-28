from __future__ import annotations

import glob
import os
import socket
from typing import Any, Sequence

import pandas as pd
from tqdm import tqdm

from .constants import sqlite_mapper, wd_mapper


def wildcard_mapper(c: str):
    if "*" in c:
        c = c.replace("*", "%")
    if "?" in c:
        c = c.replace("?", "_")
    return c


def pnwstore_filename_mapper(filename: str):
    year = int(filename.split("/")[5])
    return "/auto/pnwstore1-" + wd_mapper[year] + filename[10:]


def dummy_filename_mapper(filename: str):
    return filename


def sqlite_base():
    return sqlite_mapper[socket.gethostname()]


def dbs_mapper(year: int):
    sqlite_path = sqlite_base()
    return sqlite_path + "%d.sqlite" % year


def rst2df(result: Any, keys: str | Sequence[str] | None = None):
    if isinstance(keys, str):
        return pd.DataFrame(result, columns=[keys])
    elif isinstance(keys, list):
        return pd.DataFrame(result, columns=keys)
    else:
        return pd.DataFrame(result)


def index_folder(path: str, sqlite_path: str, mseedindex_cmd: str = "mseedindex"):
    leap_env = "LIBMSEED_LEAPSECOND_FILE=../leap-seconds.list"
    for i in tqdm(glob.glob(path + "/**/*", recursive=True)):
        if not os.path.isdir(i):
            cmd = " ".join([leap_env, mseedindex_cmd, i, "-sqlite", sqlite_path])
            os.system(cmd)
