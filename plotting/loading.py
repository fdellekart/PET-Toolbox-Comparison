"""Utilities to load metadata and timing information"""

import pandas as pd
import numpy as np


def parse_resources_file(datafile: str) -> pd.DataFrame:
    """Read resource information produced for a toolbox
    by the comparison script into a dataframe.

    :param datafile: path to a resources.csv file from a toolbox
    :return: A dataframe with columns 'time', 'n_cpus',
        'memory', 'gpu_util' 'gpu_memory', `disk_read`, `disk_written`
        Memory values are in GiB, disk read/written in GiB / s, utilization in %
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
                "Disk_Read": "disk_read",
                "Disk_Written": "disk_written",
            },
            axis=1,
        )
        .drop("memory_util", axis=1)
    )

    data["time"] = pd.to_datetime(data["time"])
    data.set_index("time", inplace=True)
    data["memory"] = data["memory"].str.split(" / ").str[0]
    is_zero_b = data["memory"] == "0B"
    data.loc[is_zero_b, "memory"] = "0GiB"
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

    data["disk_written"] = data["disk_written"].astype(np.float32) / 1000
    data["disk_read"] = data["disk_read"].astype(np.float32) / 1000

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


def prepare_for_single_frame_plot(
    resource_data: pd.DataFrame, frame_timings: pd.Series
) -> pd.DataFrame:
    """Extract frame from resource data and time everything in seconds relative to start."""
    frame_start = frame_timings["frame"]["start"]
    frame_end = frame_timings["frame"]["end"]
    is_in_frame = (resource_data.index > frame_start) & (
        resource_data.index < frame_end
    )
    resource_data = resource_data[is_in_frame]
    frame_timings = (frame_timings - frame_start).dt.seconds
    resource_data.index = (resource_data.index - frame_start).seconds

    return resource_data, frame_timings
