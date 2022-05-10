# PNWstore: Pacific NorthWest Storage
This is a python-based seismic data query and selection toolbox for users on cascadia.ess.washington.edu.

## What data are in pnwstore?
- mseed data at PNW from 1980 to 2021
- network metadata from 1980 to 2020
    - [network list here](./netlist.md)
- event metadata and phase information contributed by
    - [UW](https://pnsn.org/pnsn-data-products/earthquake-catalogs) (1980-2020)

## Why use this toolbox?
1. The waveforms stored in `mseed` can be indexed with [mseedindex](https://github.com/iris-edu/mseedindex), which would dramatically improve the efficieny of data stream. This is very useful especailly when you are working on a large amount of data. However, database system, especailly the `sqlite` that mseedindex specifies, can be hard to use sometimes, and the learning curve can be very shallow.
2. Although `xml` files contain all information of events and/or seismic networks, extra costs in codes and parsing time may not be ignored.


## Usage
### Query earthquake catalog
```python
from obspy.core.utcdatetime import UTCDateTime
from pnwstore.catalog import QuakeClient

client = QuakeClient(USERNAME, PASSWORD)

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

### Query phase picks
```python
from obspy.core.utcdatetime import UTCDateTime
from pnwstore.catalog import PickClient

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

### Query and select stream
```python
from pnwstore.mseed import WaveformClient

client = WaveformClient()

# Query all stations with channel EH? from UW network at year 2020 and doy 200.
for item in client.query(keys = 'distinct station', 
            network = "UW", channel = "EH?", year = "2020", doy = "200"):
    stations.append(item[0])


# Read with obspy and select channel
for sta in stations:
    s = obspy.read(filename_mapper(sta))
    s = s.select(channel = "EH?")
# time: 37.31 s


# Read with PNWstore index
for sta in stations:
    s = client.get_waveforms(network = "UW", 
                          station = sta, 
                          channel = "EH?", 
                          year = "2020", 
                          doy = "200")
# time: 9.24 s
```

### Query network meta
```python
from obspy.core.utcdatetime import UTCDateTime
from pnwstore.station import StationClient

client = StationClient(USERNAME, PASSWORD)
client.query("*", network = "UW", channel = "EH?",
            mintime = UTCDateTime("2010-01-15"), 
            maxtime = UTCDateTime("2000-01-16"), showquery = True)

# A pandas DataFrame is returned.
#    channel_id network station location channel  latitude  longitude elevation  depth     starttime       endtime sampling_rate azimuth 
# 0       45376      UW     SHW       --     EHZ   46.1935   -122.236   1425.00   0.00   867283200.0  1207008000.0      100.0000    None
# 1       45377      UW     SHW       --     EHZ   46.1935   -122.236   1425.00   0.00  1207008000.0  1536105600.0      100.0000    None  
```


## Database schema
PNWstore uses mysql to index all seismic data. Below are the schemas for each table.
### network schema 
```mysql
create table network (                             \
    channel_id MEDIUMINT NOT NULL AUTO_INCREMENT,  \
    network VARCHAR(3) NOT NULL,                   \
    station VARCHAR(5) NOT NULL,                   \
    location VARCHAR(3) NOT NULL,                  \
    channel CHAR(3) NOT NULL,                      \
    latitude FLOAT NOT NULL,                       \
    longitude FLOAT NOT NULL,                      \
    elevation DECIMAL(6, 2) NOT NULL,              \
    depth DECIMAL(6, 2) NOT NULL,                  \
    starttime DECIMAL(16, 1) NOT NULL,             \
    endtime DECIMAL(16, 1) NOT NULL,               \
    sampling_rate     DECIMAL(10, 4) NOT NULL,     \
    azimuth DECIMAL(5, 2),                         \
    PRIMARY KEY (channel_id)                       \
);
```
### catalog schema
```mysql
create table catalog (                             \
    source_id VARCHAR(10) NOT NULL,                \
    timestamp DECIMAL(16, 6) NOT NULL,             \
    year SMALLINT NOT NULL,                        \
    month TINYINT NOT NULL,                        \
    day TINYINT NOT NULL,                          \
    doy SMALLINT NOT NULL,                         \
    hour TINYINT NOT NULL,                         \
    minute TINYINT NOT NULL,                       \
    second TINYINT NOT NULL,                       \
    microsecond MEDIUMINT NOT NULL,                \
    latitude FLOAT NOT NULL,                       \
    longitude FLOAT NOT NULL,                      \
    depth FLOAT NOT NULL,                          \
    magnitude FLOAT NOT NULL,                      \
    contributor VARCHAR(4) NOT NULL,               \
    number_of_pick SMALLINT NOT NULL,              \
    PRIMARY KEY (source_id)                        \
);
```
### mseed schema
Note that each year relates to an individual table.
```mysql
create table mseed_YYYY (                         \
    mseed_id MEDIUMINT NOT NULL AUTO_INCREMENT,   \
    network VARCHAR(3) NOT NULL,                  \
    station VARCHAR(5) NOT NULL,                  \
    location VARCHAR(3) NOT NULL,                 \
    channel CHAR(3) NOT NULL,                     \
    quality CHAR(1) NOT NULL,                     \
    version VARCHAR(4) NOT NULL,                  \
    starttime VARCHAR(26) NOT NULL,               \
    endtime VARCHAR(26) NOT NULL,                 \
    samplerate FLOAT NOT NULL,                    \
    filename VARCHAR(48) NOT NULL,                \
    byteoffset INT NOT NULL,                      \
    bytes INT NOT NULL,                           \
    hash CHAR(32) NOT NULL,                       \
    timeindex TEXT NOT NULL,                      \
    timespans MEDIUMTEXT NOT NULL,                \
    timerates TEXT,                               \
    format TEXT,                                  \
    filemodtime VARCHAR(26) NOT NULL,             \
    updated VARCHAR(26) NOT NULL,                 \
    scanned VARCHAR(26) NOT NULL,                 \
    PRIMARY KEY (mseed_id)                        \
);
```

### pick schema
Note that each contributor relates to an individual table.
```mysql 
create table picks_CONTRIBUTOR (                  \
    pick_id INT NOT NULL AUTO_INCREMENT,          \
    source_id VARCHAR(10) NOT NULL,               \
    network VARCHAR(3) NOT NULL,                  \
    station VARCHAR(5) NOT NULL,                  \
    location VARCHAR(3) NOT NULL,                 \
    channel CHAR(3) NOT NULL,                     \
    timestamp DECIMAL(16, 6) NOT NULL,            \
    year SMALLINT NOT NULL,                       \
    month TINYINT NOT NULL,                       \
    day TINYINT NOT NULL,                         \
    doy SMALLINT NOT NULL,                        \
    hour TINYINT NOT NULL,                        \
    minute TINYINT NOT NULL,                      \
    second TINYINT NOT NULL,                      \
    microsecond MEDIUMINT NOT NULL,               \
    phase VARCHAR(6) NOT NULL,                    \
    evaluation_mode VARCHAR(10) NOT NULL,         \
    uncertainty FLOAT,                            \
    backazimuth FLOAT,                            \
    contributor VARCHAR(6) NOT NULL,              \
    PRIMARY KEY (pick_id)                         \
);"
```

## Reference
* https://pnsn.org
* https://ds.iris.edu/ds/nodes/dmc/
* https://earthquake.usgs.gov/data/comcat/
* https://github.com/iris-edu/mseedindex
