from __future__ import annotations

import io
import logging
import os
import sqlite3
from typing import Any, Callable, Iterable, Sequence

import obspy
from texttable import Texttable

from .constants import mseedkeys, wd_mapper
from .utils import dbs_mapper, pnwstore_filename_mapper, rst2df, wildcard_mapper

logging.basicConfig(level=logging.INFO, format="PNWstore | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def connect_db(year: int):
    path = dbs_mapper(year)
    db = sqlite3.connect(path)
    return db, db.cursor(), path


def connect_dbs(years: Iterable[int]):
    dbs = {}
    curs = {}
    paths = {}
    for year in years:
        dbs[year], curs[str(year)], paths[year] = connect_db(year)
    return dbs, curs, paths


class WaveformClient(object):
    def __init__(
        self,
        sqlite: str | None = None,
        filename_mapper: Callable[[str], str] | None = None,
        year: int | Iterable[int] = range(1980, 2024),
    ):
        self._sqlite = sqlite
        if sqlite:
            self._db = sqlite3.connect(sqlite)
            self._cursor = self._db.cursor()
            self._sqlite = sqlite
        else:
            if isinstance(year, int):
                self._db, self._cursor, self._sqlite = connect_db(year)
                self._year = [year]
            else:
                self._db, self._cursor, self._sqlite = connect_dbs(year)
                self._year = list(year)

        if filename_mapper:
            self._filename_mapper = filename_mapper
        else:
            self._filename_mapper = pnwstore_filename_mapper
        self._keys = mseedkeys

        for l in self._get_status()[1:]:
            if l[2] == "X":
                logger.warning("Missing database for year %s at %s", l[0], l[1])
            if l[4] == "X":
                logger.warning("Missing mount for year %s at %s", l[0], l[3])

    def _get_status(self) -> list[list[Any]]:
        """Print per-year SQLite and mount availability as a text table."""
        years = sorted(getattr(self, "_year", []))
        if not years and isinstance(self._sqlite, str):
            sqlite_name = os.path.basename(self._sqlite)
            if sqlite_name.endswith(".sqlite") and sqlite_name[:-7].isdigit():
                years = [int(sqlite_name[:-7])]

        rows: list[list[Any]] = [
            [
                "year",
                "database path",
                "",
                "mount path",
                "",
            ]
        ]

        for year in years:
            sqlite_path = (
                self._sqlite if isinstance(self._sqlite, str) else dbs_mapper(year)
            )
            sqlite_status = "OK" if os.path.exists(sqlite_path) else "X"

            if self._filename_mapper is pnwstore_filename_mapper and year in wd_mapper:
                mount_path = f"/auto/pnwstore1-{wd_mapper[year]}"
                mount_status = "OK" if os.path.isdir(mount_path) else "X"
            else:
                mount_path = "custom_filename_mapper"
                mount_status = "X"

            rows.append([year, sqlite_path, sqlite_status, mount_path, mount_status])
        return rows

    def status(self):
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_dtype(["i", "t", "t", "t", "t"])
        table.add_rows(self._get_status())
        print(table.draw())

    def query_waveforms(self, keys: str | Sequence[str] = "*", **kwargs: Any):
        rst = self._query(keys, **kwargs)
        if keys == "*":
            return rst2df(rst, self._keys)
        else:
            return rst2df(rst, keys)

    def _query(
        self, keys: str | Sequence[str] = "*", showquery: bool = False, **kwargs: Any
    ):
        if "year" not in kwargs:
            raise ValueError("year is required.")
        else:
            kwargs["year"] = str(kwargs["year"])

        if "doy" in kwargs:
            kwargs["doy"] = str(kwargs["doy"]).zfill(3)
        elif "month" in kwargs and "day" in kwargs:
            t = obspy.UTCDateTime(f'{kwargs["year"]}-{kwargs["month"]}-{kwargs["day"]}')
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
            if _k == "location" and _i == "--":
                _i = ""
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

    def get_waveforms(
        self,
        headeronly: bool = False,
        starttime: obspy.UTCDateTime | str | None = None,
        endtime: obspy.UTCDateTime | str | None = None,
        filename: str | None = None,
        **kwargs: Any,
    ):
        if starttime and endtime:
            if isinstance(starttime, str):
                starttime = obspy.UTCDateTime(starttime)
            if isinstance(endtime, str):
                endtime = obspy.UTCDateTime(endtime)
            if (starttime.year == endtime.year) and (
                starttime.julday == endtime.julday
            ):
                if starttime.year not in self._db:
                    raise ValueError(
                        f"Missing index database for year {starttime.year}"
                    )
                else:
                    kwargs["year"] = starttime.year
                    kwargs["doy"] = starttime.julday
            else:
                raise NotImplementedError(
                    "Multi-day streaming not implemented.\nStart/end time must be in the same day."
                )
        rst = self._query(["byteoffset", "bytes", "filename"], **kwargs)
        s = obspy.Stream()
        for _i in rst:
            byteoffset = _i[0]
            byte = _i[1]
            seedfile = self._filename_mapper(_i[2])
            with open(seedfile, "rb") as f:
                f.seek(byteoffset)
                buff = io.BytesIO(f.read(byte))
                try:
                    s += obspy.read(
                        buff,
                        headeronly=headeronly,
                        starttime=starttime,
                        endtime=endtime,
                    )
                except:
                    s += obspy.read(buff, headeronly=headeronly).trim(
                        starttime=starttime, endtime=endtime
                    )

        if filename:
            try:
                os.makedirs("/".join(filename.split("/")[:-1]))
            except:
                pass
            s.write(filename, format="mseed")
        else:
            return s

    def get_waveforms_bulk(
        self,
        bulk: list[
            tuple[
                str,
                str,
                str,
                str,
                obspy.UTCDateTime,
                obspy.UTCDateTime,
            ]
        ],
    ):
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
