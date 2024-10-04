import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter


resource_file = "results/2024-10-04-13-46-b9d60b5/NiftyPET/resources.csv"
metadata_file = "results/2024-10-04-13-46-b9d60b5/NiftyPET/metadata.json"


def parse_resources_file(datafile: str) -> pd.DataFrame:
    """Read resource information produced for a toolbox
    by the comparison script into a dataframe.

    :param datafile: path to a resources.csv file from a toolbox
    :return: A dataframe with columns 'memory', 'gpu_memory', 'n_cpus'
        Memory values are in GiB, utilization in %
    """
    data = (
        pd.read_csv(datafile)
        .rename(
            {
                "Timestamp": "time",
                "CPU_Usage(%)": "cpu_util",
                "Memory_Usage(%)": "memory_util",
                "Memory_Usage/Limit": "memory",
                "GPU_Memory": "gpu_memory",
                "GPU_Utilization": "gpu_util",
            },
            axis=1,
        )
        .drop("memory_util", axis=1)
    )

    data["time"] = pd.to_datetime(data["time"])
    data.set_index("time", inplace=True)
    data["memory"] = data["memory"].str.split(" / ").str[0]
    is_gigabyte = data["memory"].str.endswith("GiB")
    is_megabyte = data["memory"].str.endswith("MiB")
    assert (is_gigabyte | is_megabyte).all()
    data["memory"] = data["memory"].str[:-3].astype(np.float32)
    data.loc[is_megabyte, "memory"] = data.loc[is_megabyte, "memory"] / 1000

    data["n_cpus"] = data["cpu_util"].str[:-1].astype(np.float32) / 100
    data.drop("cpu_util", axis=1, inplace=True)

    data["gpu_util"] = data["gpu_util"].str[:-2].astype(np.float32)
    assert data["gpu_memory"].str.endswith("MiB").all()
    data["gpu_memory"] = data["gpu_memory"].str[:-4].astype(np.float32) / 1000

    return data


def parse_timings(metadata: dict) -> pd.DataFrame:
    """Extract the timing information from metadata into a dataframe.

    :param metadata: Dict loaded from the metadata.json saved for a toolbox
    :return: dataframe with one row per frame
        columns are a multiindex with first level block name and second start/end times
    """
    timings = pd.DataFrame(
        [
            {
                (block_name, inner_key): value
                for block_name, inner_dict in frame.items()
                for inner_key, value in inner_dict.items()
            }
            for frame in metadata["timings"]
        ]
    ).map(pd.to_datetime)
    timings.columns = pd.MultiIndex.from_tuples(timings.columns)
    return timings


with open(metadata_file) as f:
    metadata = json.load(f)


class MyFormatter(Formatter):
    def __call__(self, x, pos=0):
        minutes = int(x // 60)
        seconds = int(x % 60)
        return f"{'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}"


def plot_frame(resource_data: pd.DataFrame, frame_timings: pd.Series) -> None:
    is_in_frame = (resource_data.index > frame_timings["frame"]["start"]) & (
        resource_data.index < frame_timings["frame"]["end"]
    )
    resource_data = resource_data[is_in_frame]
    resource_data.index = (resource_data.index - resource_data.index.min()).seconds

    fig, ((cpu_ax, mem_ax), (gpu_util_ax, gpu_mem_ax)) = plt.subplots(2, 2)

    cpu_ax.set_title("Number of used CPU cores")
    mem_ax.set_title("RAM usage in GB")
    gpu_util_ax.set_title("GPU utilization in %")
    gpu_mem_ax.set_title("GPU memory usage in GB")

    cpu_ax.plot(resource_data.index, resource_data["n_cpus"])
    mem_ax.plot(resource_data.index, resource_data["memory"])
    gpu_util_ax.plot(resource_data.index, resource_data["gpu_util"])
    gpu_mem_ax.plot(resource_data.index, resource_data["gpu_memory"])

    cpu_ax.xaxis.set_major_formatter(MyFormatter())
    mem_ax.xaxis.set_major_formatter(MyFormatter())
    gpu_util_ax.xaxis.set_major_formatter(MyFormatter())
    gpu_mem_ax.xaxis.set_major_formatter(MyFormatter())

    cpu_ax.set_ylim(bottom=0)
    mem_ax.set_ylim(bottom=0)
    gpu_util_ax.set_ylim(bottom=0)
    gpu_mem_ax.set_ylim(bottom=0)

    cpu_ax.set_xticks(
        np.arange(resource_data.index.min(), resource_data.index.max(), 60)
    )
    cpu_ax.set_xticklabels(cpu_ax.get_xticklabels(), rotation=50)

    plt.tight_layout()
    plt.show()


resource_data = parse_resources_file(resource_file)
timings = parse_timings(metadata)
plot_frame(resource_data, timings.loc[1, :])
