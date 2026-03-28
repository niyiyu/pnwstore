import glob
import os

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

mseedindex_cmd = "mseedindex"
path = "/data/wsd01/HOOD_data"
sqlite_path = "/data/wsd01/HOOD_data/mseed.sqlite"
leap_env = "LIBMSEED_LEAPSECOND_FILE=../leap-seconds.list"

for idx, i in enumerate(glob.glob(path + "/**/*", recursive=True)):
    if idx % size == rank:
        if not os.path.isdir(i):
            cmd = " ".join([leap_env, mseedindex_cmd, i, "-sqlite", sqlite_path])
            os.system(cmd)
