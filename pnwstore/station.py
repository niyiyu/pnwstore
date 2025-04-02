import mysql.connector
import obspy

from .utils import rst2df, wildcard_mapper


class StationClient(object):
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

    def query(self, keys="*", showquery=False, **kwargs):
        if hasattr(self, "_keys"):
            pass
        else:
            self._cursor.execute(f"SHOW COLUMNS FROM network;")
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
        query_str += " FROM network "
        _qs = []
        for _k, _i in kwargs.items():
            if isinstance(_i, str):
                if "_" in _i or "%" in _i:
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

            elif isinstance(_i, obspy.UTCDateTime):
                if _k == "time":
                    _q = f"(starttime <= {_i.timestamp + 86400 - 1} AND endtime >= {_i.timestamp})"
                else:
                    if _k == "mintime":
                        _q = f"starttime <= {_i.timestamp}"
                    elif _k == "maxtime":
                        _q = f"endtime >= {_i.timestamp}"
                _qs.append(_q)
            else:
                raise ValueError(f"Unsupported query key <{_k}>: {_i}")

        if len(_qs) != 0:
            query_str += " WHERE "
            if len(_qs) == 1:
                query_str += _qs[0]
            else:
                query_str += " AND ".join(_qs)
        query_str += ";"
        if showquery:
            print(query_str)
        self._cursor.execute(query_str)

        result = self._cursor.fetchall()
        if "*" in query_key:
            return rst2df(result, self._keys)
        else:
            return rst2df(result, keys)
