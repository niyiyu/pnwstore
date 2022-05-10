import pandas as pd


def year2day(quake_year):
    if quake_year == 2010:
        return 8
    else:
        return abs(quake_year - 2031) % 11


def wildcard_mapper(c):
    if "*" in c:
        c = c.replace("*", "%")
    if "?" in c:
        c = c.replace("?", "_")
    return c


def filename_mapper(filename):
    return "/1-fnp/pnwstore1/p-" + filename[6:]


def dbs_mapper(year):
    sqlite_path = "/data/wsd01/PNWstore_sqlite/"
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
