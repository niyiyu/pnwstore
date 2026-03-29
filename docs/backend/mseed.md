# miniSEED Storage

## Storage

All miniSEED files are stored on `pnwstore1.ess.washington.edu` under the directory `/data` and named by the data year. The data are organized so that multiple years may fill in a single drive/partition of 15 TB. The `/data/wd11` directory is used for station (`/data/wd11/PNWStationXML`) and event (`/data/wd11/PNWQuakeML`) metadata.

```bash
tree /data -L 2
.
├── wd00
│   ├── PNW1987
│   ├── PNW1998
│   ├── PNW2009
│   └── PNW2020
├── wd01
│   ├── PNW1986
│   ├── PNW1997
│   ├── PNW2008
│   └── PNW2019
├── wd02
│   ├── PNW1985
│   ├── PNW1989
│   ├── PNW1996
│   ├── PNW2007
│   ├── PNW2011
│   └── PNW2018
├── wd03
│   ├── PNW1984
│   ├── PNW1995
│   ├── PNW2006
│   └── PNW2022
├── wd04
│   ├── PNW1983
│   ├── PNW1994
│   └── PNW2005
├── wd05
│   ├── PNW1982
│   ├── PNW1993
│   ├── PNW2000
│   ├── PNW2004
│   ├── PNW2015
│   └── PNW2016
├── wd06
│   ├── PNW1981
│   ├── PNW1992
│   ├── PNW2003
│   └── PNW2014
├── wd07
│   ├── PNW1980
│   ├── PNW1991
│   ├── PNW2002
│   ├── PNW2013
│   └── PNW2017
├── wd08
│   ├── PNW1990
│   ├── PNW2001
│   ├── PNW2010
│   └── PNW2012
├── wd09
│   └── PNW2023
├── wd10
│   ├── PNW1988
│   ├── PNW1999
│   └── PNW2021
└── wd11
    ├── PNWQuakeML
    └── PNWStationXML
```

For each year, the files are organized as `<network>/<year>/<day-of-year>/<station>.<network>.<year>.<day-of-year>`. For example, the file for UW station VLL on Jan 1, 2020 is located at `/data/wd00/PNW2020/UW/2020/001/VLL.UW.2020.001`. All locations and channels are saved in the same files.

A `timeseries.sqlite` database is also stored under each year directory, which indexes the miniSEED files for that specific year. The database is generated using the `mseedindex` tool (see [here](https://github.com/EarthScope/mseedindex) for more details). PNWstore uses these databases to query byte ranges for specific channels and time ranges, which allows for efficient retrieval of miniSEED data without having to read entire files (save bandwidth when accessing data through cross-mount/ethernet).

## Cross-mounting
Most group machines have cross-mount configured to access pnwstore1 through ethernet. Mounting points are commonly saved at `/1-fnp` as symbolic links but can be configured at `/etc/auto.auto` (sudo required). Through cross-mounting, users can access files as if they were local. However, a path mapping is needed. For example, the above path to the VLL station file on Jan 1, 2020 would be accessed as `/1-fnp/pnwstore1/p-wd00/PNW2020/UW/2020/001/VLL.UW.2020.001`.

For efficient query, database files are copied locally on each machine. See [here](https://github.com/niyiyu/pnwstore/blob/899bc6c36520adde181a5727ecc3343bc46230c1/pnwstore/constants.py#L48-L53) for the paths.

## Check Status
The `WaveformClient` has a `status` method that reports database and cross mount status. Here, one can see that the cross-mount for `wd09` failed (shown as `X`).

```python
>>> from pnwstore import WaveformClient
>>> client = WaveformClient()
>>> client.status()

year |          database path           |    |      mount path      |
=====+==================================+====+======================+===
1980 | /wd1/PNWstore_sqlite/1980.sqlite | OK | /auto/pnwstore1-wd07 | OK
1981 | /wd1/PNWstore_sqlite/1981.sqlite | OK | /auto/pnwstore1-wd06 | OK
...
2022 | /wd1/PNWstore_sqlite/2022.sqlite | OK | /auto/pnwstore1-wd03 | OK
2023 | /wd1/PNWstore_sqlite/2023.sqlite | OK | /auto/pnwstore1-wd09 | X
```
