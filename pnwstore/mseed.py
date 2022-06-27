import sqlite3
import obspy
import io
import asyncio

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
    def __init__(self, year=range(1980, 2021)):
        if isinstance(year, int):
            self._db, self._cursor = connect_db(year)
            self._year = [year]
        else:
            self._db, self._cursor = connect_dbs(year)
            self._year = list(year)
        self._keys = mseedkeys()

    def query_waveforms(self, keys="*", **kwargs):
        rst = self.query(keys, **kwargs)
        if keys == "*":
            return rst2df(rst, self._keys)
        else:
            return rst2df(rst, keys)

    def query(self, keys="*", showquery=False, **kwargs):
        if "year" not in kwargs:
            raise ValueError("year is required.")
        else:
            kwargs["year"] = str(kwargs["year"])

        if "doy" in kwargs:
            kwargs["doy"] = str(kwargs["doy"]).zfill(3)
        elif "month" in kwargs and "day" in kwargs:
            t = obspy.core.utcdatetime.UTCDateTime(
                f'{kwargs["year"]}-{kwargs["month"]}-{kwargs["day"]}'
            )
            kwargs["doy"] = str(t.julday).zfill(3)
            del kwargs["month"], kwargs["day"]
        else:
            raise ValueError("Either month/day or doy is required.")

        query_str = "SELECT "
        if isinstance(keys, str):
            query_key = keys
        else:
            if len(keys) > 0:
                query_key = ", ".join(keys)
            else:
                query_key = "*"

        query_str += query_key
        query_str += " FROM tsindex"
        _qs = []
        for _k, _i in kwargs.items():
            if "_" in _i or "%" in _i or "-" in _i:
                raise ValueError("Only wildcards ? and * are supported.")
            else:
                if _k in ["station", "network", "location", "channel"]:
                    if "?" not in _i and "*" not in _i:
                        _q = f"{_k} = '{_i}'"
                    else:
                        _q = f"{_k} LIKE '{wildcard_mapper(_i)}'"
                    _qs.append(_q)
                elif _k in ["doy", "year"]:
                    _q = f"filename LIKE '%%/{_i}/%%'"
                    _qs.append(_q)
                else:
                    raise ValueError

        if len(_qs) != 0:
            query_str += " WHERE "
            if len(_qs) == 1:
                query_str += _qs[0]
            else:
                query_str += " AND ".join(_qs)
        if showquery:
            print(query_str)
        if isinstance(self._cursor, dict):
            return self._cursor[kwargs["year"]].execute(query_str)
        else:
            return self._cursor.execute(query_str)

    def get_waveforms(self, headeronly=False, **kwargs):
        rst = self.query(["byteoffset", "bytes", "filename"], **kwargs)
        s = obspy.Stream()
        for _i in rst:
            byteoffset = _i[0]
            byte = _i[1]
            seedfile = filename_mapper(_i[2])
            with open(seedfile, "rb") as f:
                f.seek(byteoffset)
                buff = io.BytesIO(f.read(byte))
                s += obspy.read(buff, headeronly=headeronly)
        return s

    def get_waveforms_bulk(self, bulk):
        """
        Follow the API of obspy.clients.fdsn.client.Client.get_waveforms_bulk
        """
        if isinstance(bulk, list):
            s = obspy.Stream()
            for _b in bulk:
                net, sta, loc, cha, st, et = _b

                # TODO: work on multiple days
                assert st.year == et.year
                assert st.julday == et.julday

                year = st.year
                doy = st.julday
                tr = self.get_waveforms(
                    network=net,
                    station=sta,
                    location=loc,
                    channel=cha,
                    year=year,
                    doy=doy,
                )
                tr.trim(starttime=st, endtime=et)
                s += tr

        return s
