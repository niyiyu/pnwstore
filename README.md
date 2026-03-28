# PNWstore: Pacific Northwest Storage
[![DOI](https://zenodo.org/badge/479659348.svg)](https://zenodo.org/badge/latestdoi/479659348) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a python-based seismic data query and selection toolbox for [Denolle-lab](https://denolle-lab.github.io) members. The server runs at https://pnwstore1.ess.washington.edu/ and is only accessible within the UW network.

The pnwstore documentation can be found [here](https://niyiyu.github.io/pnwstore).

## What data are in pnwstore?
- mseed data from PNW (1980 - 2023)
- network metadata (1980 - 2022)
    - [network list](https://niyiyu.github.io/pnwstore/network_list.html)
- earthquake catalog contributed by
    - [Pacific Northwest Seismic Network](https://pnsn.org/pnsn-data-products/earthquake-catalogs) (1980-2022)
- list of known data issues could be found [here](https://niyiyu.github.io/pnwstore/data_issue.html).

## Why use this package?
1. The waveforms stored in `.mseed` are indexed with [mseedindex](https://github.com/iris-edu/mseedindex), which would dramatically improve data loading efficiency. This is very useful especially when working with large amounts of data.
2. `.xml` files contain all events and station metadata, but loading and parsing them requires extra time. It is recommended to extract key informations and index them in a database system.
3. The pnwstore client emulates the ObsPy FDSN client so that transition to the local data requires little changes to the codebase.

## Usage
### Get waveform data
```python
from obspy import UTCDateTime
from pnwstore import WaveformClient
client = WaveformClient()

starttime = UTCDateTime("2020-01-01T00:00:00")
endtime = starttime + 3600
s = client.get_waveforms(network="UW", station="SHW", channel="EH?",
                         starttime=starttime, endtime=endtime)
```

### Get event catalog
```python
from obspy import UTCDateTime
from pnwstore import EventClient

client = EventClient(USERNAME, PASSWORD)

client.query(mintime = UTCDateTime("1980-01-01T00:00:00"),
             maxtime = UTCDateTime("2021-01-01T00:00:00"),
             minlatitude = 40,    maxlatitude = 50,
             minlongitude = -128, maxlongitude = -120,
             minmagnitude = 5.9)

# A pandas DataFrame is returned.
#   source_id   origin_timestamp year month day doy hour minute second  microsecond latitude longitude  depth  magnitude contributor number_of_pick
# 0 uw10313718  748582000.0      1993 9     21  264 3    26     55      630000      42.316    -122.027  8.560  5.9       uw          380
# 1 uw10313838  748590000.0      1993 9     21  264 5    45     35      230000      42.358    -122.058  8.530  6.0       uw          427
# 2 uw10530748  983386000.0      2001 2     28  59  18   54     32      830000      47.149    -122.727  51.798 6.8       uw          98

```

### Get picks
```python
from obspy import UTCDateTime
from pnwstore import PickClient

client = PickClient(USERNAME, PASSWORD)

client.query(network = "UW", station = "SHW", phase = "P*",
             mintime = UTCDateTime("2000-01-01"),
             maxtime = UTCDateTime("2000-01-10"))

# A pandas DataFrame is returned.
#   pick_id   source_id network station location channel    timestamp  year month day doy  hour  minute  second  microsecond phase evaluation_mode uncertainty  backazimuth contributor
# 0 1133412  uw10485733      UW     SHW       --     EHZ  947343000.0  2000   1    8    8    14      57      23       680000     P          manual   0.05         79.0          UW
# 1 1133508  uw10485213      UW     SHW       --     EHZ  947142000.0  2000   1    6    6     6      52      56       790000     P          manual   0.08         63.6          UW
# 2 1133612  uw10484688      UW     SHW       --     EHZ  946890000.0  2000   1    3    3     9       0      14       280000     P          manual   0.22        222.1          UW
```

### Get station metadata
```python
from obspy import UTCDateTime
from pnwstore import StationClient

client = StationClient(USERNAME, PASSWORD)
client.query(network = "UW", channel = "EH?",
             mintime = UTCDateTime("2010-01-15"),
             maxtime = UTCDateTime("2000-01-16"))

# A pandas DataFrame is returned.
#    channel_id network station location channel  latitude  longitude elevation  depth     starttime       endtime sampling_rate azimuth
# 0       45376      UW     SHW       --     EHZ   46.1935   -122.236   1425.00   0.00   867283200.0  1207008000.0      100.0000    None
# 1       45377      UW     SHW       --     EHZ   46.1935   -122.236   1425.00   0.00  1207008000.0  1536105600.0      100.0000    None
```

---


## Reference
* https://pnsn.org
* https://ds.iris.edu/ds/nodes/dmc/
* https://earthquake.usgs.gov/data/comcat/
* https://github.com/iris-edu/mseedindex
