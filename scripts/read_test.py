from pnwstore import WaveformClient

client = WaveformClient()

for year in range(1980, 2023):
    print(year, client.get_waveforms(network = "UW", station = "SHW", year = year, doy=1))