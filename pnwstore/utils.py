sqlite_path = "~/.pnwstore/mseed/"


def year2day(quake_year):
    return abs(quake_year - 2020) % 11


def wildcard_mapper(c):
    if "*" in c:
        c = c.replace("*", "%")
    if "?" in c:
        c = c.replace("?", "_")
    return c


def filename_mapper(filename):
    return "/1-fnp/pnwstore1/p-" + filename[6:]


def dbs_mapper(year):
    return sqlite_path + "%d.sqlite" % year
