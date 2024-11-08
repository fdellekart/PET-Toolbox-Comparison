"""Utilities to load metadata and timing information"""

from typing import Tuple

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
    resource_data: pd.DataFrame, frame_timings: pd.DataFrame, frame_index: int
) -> Tuple[pd.DataFrame, pd.Series]:
    """Extract frame from resource data and time everything in seconds relative to start.

    :param resource_data: DataFrame with DatetimeIndex
    :param frame_timings: Timing information for all frames as loaded from resources.csv
    :param frame_index: Index of the frame to create the plot for
    :return: resource_data: Extracted data for specified frame
                            with index in seconds from frame start
             single_frame_timings: Timing information of the frame
    """
    single_frame_timings = frame_timings.loc[frame_index, :]
    frame_start = single_frame_timings["frame"]["start"]
    frame_end = single_frame_timings["frame"]["end"]
    is_in_frame = (resource_data.index > frame_start) & (
        resource_data.index < frame_end
    )
    resource_data = resource_data[is_in_frame]
    single_frame_timings = (single_frame_timings - frame_start).dt.seconds
    resource_data.index = (resource_data.index - frame_start).seconds

    return resource_data, single_frame_timings
