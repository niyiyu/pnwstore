# PNWstore: Pacific NorthWest Storage
This is a python-based seismic data query and selection toolbox for users on cascadia.ess.washington.edu.

## What data are in pnwstore?
- mseed data at PNW from 1980 to 2020
- network metadata from 1980 to 2020
    - [network/station list here](./netlist.md)
- event metadata and phase information contributed by
    - [UW](https://pnsn.org/pnsn-data-products/earthquake-catalogs) (1980-2020)

## Why use this toolbox?
1. The waveforms stored in `mseed` can be indexed with [mseedindex](https://github.com/iris-edu/mseedindex), which would dramatically improve the efficieny of data stream. This is very useful especailly when you are working on a large amount of data. However, database system, especailly the `sqlite` that mseedindex specifies, can be hard to use sometimes, and the learning curve can be very shallow.
2. Although `xml` files contain all information of events and/or seismic networks, extra costs in codes and parsing time may not be ignored.


## Usage
### Query phase picks
```python
from obspy.core.utcdatetime import UTCDateTime
from pnwstore.catalog import PickClient

client = PickClient(USERNAME, PASSWORD)

client.query(network = "UW", station = "SHW", phase = "P*",
    mintime = UTCDateTime("2000-01-01"), maxtime = UTCDateTime("2000-01-10"))

# A pandas DataFrame is returned.
#    pick_id   source_id network station location channel    timestamp  year month day doy  hour  minute  second  microsecond phase evaluation_mode uncertainty  backazimuth contributor 
# 0  1133412  uw10485733      UW     SHW       --     EHZ  947343000.0  2000   1    8    8    14      57      23       680000     P          manual   0.05         79.0          UW
# 1  1133508  uw10485213      UW     SHW       --     EHZ  947142000.0  2000   1    6    6     6      52      56       790000     P          manual   0.08         63.6          UW 
# 2  1133612  uw10484688      UW     SHW       --     EHZ  946890000.0  2000   1    3    3     9       0      14       280000     P          manual   0.22        222.1          UW 
```



### Query and select stream
```python
from pnwstore.mseed import WaveformClient

client = WaveformClient()

# Query all stations with channel EH? from UW network at year 2020 and doy 200.
for item in client.query('distinct station', network = "UW", channel = "EH?", year = "2020", doy = "200"):
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

## Database schema
PNWstore uses mysql to index all seismic data. Below are the schemas for each table.
### network schema 
```mysql
create table network (                             \
    channel_id MEDIUMINT NOT NULL AUTO_INCREMENT,  \
    network_code VARCHAR(3) NOT NULL,              \
    station_code VARCHAR(5) NOT NULL,              \
    location_code VARCHAR(3) NOT NULL,             \
    channel_code CHAR(3) NOT NULL,                 \
    station_latitude_deg FLOAT NOT NULL,           \
    station_longitude_deg FLOAT NOT NULL,          \
    station_depth_km FLOAT NOT NULL,               \
    station_starttime FLOAT NOT NULL,              \
    station_endtime FLOAT NOT NULL,                \
    trace_sampling_rate_hz SMALLINT NOT NULL,      \
    azimuth_deg FLOAT,                             \
    PRIMARY KEY (channel_id)                       \
);
```
### catalog schema
```mysql
create table catalog (                             \
    source_id VARCHAR(10) NOT NULL,                \
    source_origin_time FLOAT NOT NULL,             \
    source_latitude_deg FLOAT NOT NULL,            \
    source_longitude_deg FLOAT NOT NULL,           \
    source_depth_km FLOAT NOT NULL,                \
    source_magnitude FLOAT NOT NULL,               \
    source_contributor VARCHAR(4) NOT NULL,        \
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
    timestamp FLOAT NOT NULL,                     \
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