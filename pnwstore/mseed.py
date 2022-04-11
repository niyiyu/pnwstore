import sqlite3
import obspy
import io
from .utils import *


def connect_db(year):
    db = sqlite3.connect(dbs_mapper(year))
    return db, db.cursor()


def connect_dbs(years):
    dbs = {}
    curs = {}
    for _y in years:
        dbs[_y] = sqlite3.connect(dbs_mapper(_y))
        curs[str(_y)] = dbs[_y].cursor()
    return dbs, curs




class WaveformClient(object):
    def __init__(self, year = range(1980, 2021)):
        if isinstance(year, int):
            self._db, self._cursor = connect_db(year)
            self._year = [year]
        else:
            self._db, self._cursor = connect_dbs(year)
            self._year = list(year)
        
    def query(self, keys = "*", showquery=False, **kwargs):
        if 'year' not in kwargs:
            raise ValueError("Year is a required argument.")
        query_str = "select "
        if isinstance(keys, str):
            query_str += keys
        else:
            if len(keys) > 0:
                query_str += ", ".join(keys)
            else:
                query_str += "*"
        query_str += " from tsindex"
        _qs = []
        for _k, _i in kwargs.items():
            if "_" in _i or "%" in _i or "-" in _i:
                raise ValueError("Only wildcards ? and * are supported.")
            else:
                if _k in ["station", "network", "location", "channel"]:
                    if "?" not in _i and "*" not in _i:
                        _q = "%s = '%s'" % (_k, _i)
                    else:
                        _q = "%s like '%s'" % (_k, wildcard_mapper(_i))
                    _qs.append(_q)
                elif _k in ["doy", "year"]:
                    _q = "filename like '%%.%s%%'" % _i
                    _qs.append(_q)
                else:
                    raise ValueError

        if len(_qs) != 0:
            query_str += " where "
            if len(_qs) == 1:
                query_str += _qs[0]
            else:
                query_str += " and ".join(_qs)
        if showquery:
            print(query_str)
        if isinstance(self._cursor, dict):
            return self._cursor[kwargs['year']].execute(query_str)
        else:
            return self._cursor.execute(query_str)


    def get_waveforms(self, headeronly = False, **kwargs):
        rst = self.query(["byteoffset", "bytes", "filename"], **kwargs)
        s = obspy.Stream()
        for _i in rst:
            byteoffset = _i[0]
            byte = _i[1]
            seedfile = filename_mapper(_i[2])
            with open(seedfile, "rb") as f:
                f.seek(byteoffset)
                buff = io.BytesIO(f.read(byte))
                s += obspy.read(buff, headeronly = headeronly)
        return s