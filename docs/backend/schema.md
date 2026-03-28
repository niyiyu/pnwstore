## Database Schema
PNWstore uses mysql to index all seismic data. Below are the schemas for each table.

### Network Schema
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
### Catalog Schema
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
    magnitude_type VARCHAR(2) NOT NULL,            \
    contributor VARCHAR(4) NOT NULL,               \
    number_of_pick SMALLINT NOT NULL,              \
    PRIMARY KEY (source_id)                        \
);
```
### Mseed Schema
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

### Pick Schema
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
    onset VARCHAR(2),                             \
    polarity VARCHAR(2),                          \
    uncertainty FLOAT,                            \
    backazimuth FLOAT,                            \
    contributor VARCHAR(6) NOT NULL,              \
    PRIMARY KEY (pick_id)                         \
);"
```
