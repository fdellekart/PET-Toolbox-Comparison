import pandas as pd

from plotting.plot import plot_cpu_ram, plot_disk, plot_gpu

jsrecon_path = "results/JSRecon/resources_e7_recon_recon.csv"

data = pd.read_csv(jsrecon_path).rename(
    {
        "cpu_cores": "n_cpus",
        "disk_write": "disk_written",
    },
    axis=1,
)
data["memory"] = data["memory"] / 1000
data["gpu_memory"] = data["gpu_memory"] / 1000
data["time"] = pd.to_datetime(data["time"])
data["time"] = (data["time"] - data["time"].min()).dt.seconds
data.set_index("time", inplace=True)

frame_timings = pd.Series(
    [0, data.index.max()],
    index=pd.MultiIndex.from_tuples([("frame", "start"), ("frame", "end")]),
)

plot_cpu_ram(data, frame_timings)
plot_gpu(data, frame_timings)
plot_disk(data, frame_timings)
