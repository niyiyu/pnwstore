# PNWstore: Pacific NorthWest Storage
This is a python-based seismic data query and selection toolbox for users on cascadia.ess.washington.edu.

## What data are in pnwstore?
- mseed data at PNW from 1980 to 2020
- network metadata from 1980 to 2020
    - [network/station list here](./netlist.md)
- event metadata from 1980 to 2020 contributed by
    - [UW](https://pnsn.org/pnsn-data-products/earthquake-catalogs)  

## Why use this toolbox?
1. The waveforms stored in `mseed` can be indexed with [mseedindex](https://github.com/iris-edu/mseedindex), which would dramatically improve the efficieny of data stream. This is very useful especailly when you are working on a large amount of data. However, database system, especailly the `sqlite` that mseedindex specifies, can be hard to use sometimes, and the learning curve can be very shallow.
2. Although `xml` files contain all information of events and/or seismic networks, extra costs in codes and parsing time may not be ignored.


## Usage
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
create table network (     \
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
create table catalog (     \
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
create table mseed_YYYY (      \
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