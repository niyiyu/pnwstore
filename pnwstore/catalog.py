import mysql.connector
from numpy import isin
from obspy.core.utcdatetime import UTCDateTime

from .utils import *


class QuakeClient(object):
    def __init__(
        self,
        user,
        password,
        host="pnwstore1.ess.washington.edu",
        database="PNW",
    ):
        self._db = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self._cursor = self._db.cursor()

    def query(self, keys="source_id", showquery=False, **kwargs):
        query_str = "SELECT "

        if isinstance(keys, str):
            query_str += keys
        else:
            if len(keys) > 0:
                query_str += ", ".join(keys)
            else:
                query_str += "*"

        query_str += " FROM catalog "
        _qs = []
        for _k, _i in kwargs.items():
            if _k == "starttime":
                if isinstance(_i, UTCDateTime):
                    _qs.append(f"source_origin_time >= {_i.timestamp}")
                else:
                    _qs.append(f"source_origin_time >= {UTCDateTime(_i).timestamp}")
            elif _k == "endtime":
                if isinstance(_i, UTCDateTime):
                    _qs.append(f"source_origin_time <= {_i.timestamp}")
                else:
                    _qs.append(f"source_origin_time <= {UTCDateTime(_i).timestamp}")
            elif _k == "contributor":
                _qs.append(f"source_contributor = '{_i}'")
            elif _k == "minlatitude":
                _qs.append(f"source_latitude_deg >= {_i}")
            elif _k == "maxlatitude":
                _qs.append(f"source_latitude_deg <= {_i}")
            elif _k == "minlongitude":
                _qs.append(f"source_longitude_deg >= {_i}")
            elif _k == "maxlongitude":
                _qs.append(f"source_longitude_deg <= {_i}")
            elif _k == "mindepth":
                _qs.append(f"source_depth_km >= {_i}")
            elif _k == "maxdepth":
                _qs.append(f"source_depth_km <= {_i}")

        if len(_qs) != 0:
            query_str += " WHERE "
            if len(_qs) == 1:
                query_str += _qs[0]
            else:
                query_str += " and ".join(_qs)
        query_str += ";"
        if showquery:
            print(query_str)
        self._cursor.execute(query_str)

        return self._cursor.fetchall()


class PickClient(object):
    def __init__(
        self,
        user,
        password,
        host="pnwstore1.ess.washington.edu",
        database="PNW",
        contributor="UW",
    ):
        self._db = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self._contributor = contributor
        self._cursor = self._db.cursor()
        self._cursor.execute("SHOW TABLES;")
        self._table_avail = []
        for _i in self._cursor.fetchall():
            if "picks_" in _i[0]:
                self._table_avail.append(_i[0])
        if f"picks_{self._contributor.lower()}" not in self._table_avail:
            raise ValueError(f"Unsupported <contributor>: {self._contributor.lower()}.")
        else:
            self._table = f"picks_{self._contributor.lower()}"

    def query(self, keys="*", showquery=False, **kwargs):
        if hasattr(self, "_keys"):
            pass
        else:
            self._cursor.execute(f"SHOW COLUMNS FROM {self._table};")
            self._keys = [i[0] for i in self._cursor.fetchall()]

        query_str = "SELECT "
        if isinstance(keys, str):
            query_key = keys
        else:
            if len(keys) > 0:
                query_key = ", ".join(keys)
            else:
                query_key = "*"

        query_str += query_key
        query_str += f" FROM {self._table} "

        _qs = []
        for _k, _i in kwargs.items():
            if isinstance(_i, str):
                if "_" in _i or "%" in _i or "-" in _i:
                    raise ValueError("Only wildcards ? and * are supported.")
                else:
                    if _k in [
                        "station",
                        "network",
                        "location",
                        "channel",
                        "evaluation_mode",
                        "source_id",
                    ]:
                        if "?" not in _i and "*" not in _i:
                            _q = f"{_k} = '{_i}'"
                        else:
                            _q = f"{_k} LIKE '{wildcard_mapper(_i)}'"
                        _qs.append(_q)
                    elif _k == "phase":
                        if "?" not in _i and "*" not in _i:
                            _q = f"{_k} = '{_i.upper()}'"
                        else:
                            _q = f"{_k} LIKE '{wildcard_mapper(_i)}'"
                        _qs.append(_q)
                    else:
                        raise ValueError(f"Unsupported query key <{_k}>: {_i}")

            elif isinstance(_i, UTCDateTime):
                if _k == "mintime":
                    _q = f"timestamp >= {_i.timestamp}"
                elif _k == "maxtime":
                    _q = f"timestamp <= {_i.timestamp}"
                _qs.append(_q)
            else:
                raise ValueError(f"Unsupported query key <{_k}>: {_i}")

        if len(_qs) != 0:
            query_str += " WHERE "
            if len(_qs) == 1:
                query_str += _qs[0]
            else:
                query_str += " and ".join(_qs)
        query_str += ";"
        if showquery:
            print(query_str)

        self._cursor.execute(query_str)

        result = self._cursor.fetchall()
        if "*" in query_key:
            return rst2df(result, self._keys)
        else:
            return rst2df(result, keys)
