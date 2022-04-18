import mysql.connector
from numpy import isin
from obspy.core.utcdatetime import UTCDateTime


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
