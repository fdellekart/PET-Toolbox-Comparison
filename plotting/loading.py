"""Utilities to load metadata and timing information"""

import os
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np


E7_LOG_START_OF_MSG_COL_IDX = 39


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


def fix_e7_log_column_lengths(
    filepath: Path, fixed_col_length_file: Path, force: bool = False
) -> None:
    """So that e7 logs can be read with pd.read_fwf,
    message column is padded with whitespace where messages
    are shorter than the maximum message length.
    First line is removed from the log.

    :param filepath: Path to e7 tools log ouput
    :param transformed_filepath: Path to write result to
    :param force: Do not skip if transformed file exists
    """
    if not os.path.exists(fixed_col_length_file) or force:
        with open(filepath, "r") as f:
            next(f)  # Drop header
            log_lines = f.readlines()

        max_msg_col_length = max(len(line) for line in log_lines)

        with open(fixed_col_length_file, "w") as f:
            for original_line in log_lines:
                msg_col_length = len(original_line) - E7_LOG_START_OF_MSG_COL_IDX
                new_line = (
                    original_line[:-1]
                    + " " * (max_msg_col_length - msg_col_length)
                    + "\n"
                )
                f.write(new_line)


def load_e7_fixed_col_length_file(path: Path) -> pd.DataFrame:
    """Load the transformed file and perform preprocessing.

    :param path: Preprocessed file with a constant column length
    :return: dataframe with time index and colums msg_type, msg
    """
    with open(path, "r") as f:
        max_msg_col_length = len(f.readline())

    return (
        pd.read_fwf(path, colspecs=[(0, 1), (2, 25), (38, max_msg_col_length)])
        .set_axis(["msg_type", "time", "msg"], axis=1)
        .astype({"time": "datetime64[ns]"})
        .set_index("time")
        .assign(msg=lambda df: df.msg.str.strip())
    )


def load_e7_recon_timings(fixed_col_length_file: Path) -> pd.DataFrame:
    """Parse e7 tools log file into common dataframe
    with duration information of frames

    :param fixed_col_length_file: Preprocessed file with a constant colum length
    :return: Dataframe with frame timings
    """
    data = load_e7_fixed_col_length_file(fixed_col_length_file)
    msg = data["msg"]

    cond_start = msg.str.startswith("axis table=4084").fillna(False)
    cond_end = msg.str.startswith("finished calculation of image").fillna(False)

    frame_starts = data[cond_start].index
    frame_ends = data[cond_end].index

    cond_start = msg.str.contains("estimate scatter sinogram").fillna(False)
    cond_end = msg.str.contains("End Scatter Simulation Iteration 2").fillna(False)
    scatter_starts = data[cond_start].index
    scatter_ends = data[cond_end].index

    cond_start = msg.str.contains("start calculation of image").fillna(False)
    cond_end = msg.str.contains("finished calculation of image").fillna(False)
    recon_starts = data[cond_start].index
    recon_ends = data[cond_end].index

    return pd.DataFrame(
        data={
            ("frame", "start"): frame_starts,
            ("frame", "end"): frame_ends,
            ("scatter", "start"): scatter_starts,
            ("scatter", "end"): scatter_ends,
            ("recon", "start"): recon_starts,
            ("recon", "end"): recon_ends,
        }
    )


def load_e7_histo_timings(fixed_col_length_file: Path) -> pd.DataFrame:
    """Load timings for histogramming form log.
    The data is returned in the dataframe as 'frame' as the first
    level of the multiindex to be compatible with 'prepare_for_single_frame_plot'.

    :param fixed_col_length_file: Preprocessed file with a constant colum length
    """
    data = load_e7_fixed_col_length_file(fixed_col_length_file)
    msg = data["msg"]

    cond_start = msg.str.contains("Sinogram no =")
    cond_end = msg.str.contains("Frame_write: Just sent Frame")

    histo_starts = data.index[600:][cond_start[600:]][::2]
    histo_ends = data[cond_end].index[1:]

    return pd.DataFrame(
        data={
            ("frame", "start"): histo_starts,
            ("frame", "end"): histo_ends,
        }
    )


def parse_e7_resource_file(resources_path: Path) -> pd.DataFrame:
    """Load the resource log created by the powershell script
    running in parallel to the e7-tools reconstruction. The format
    is slightly different from what the Linux version uses just
    because I didn't bother to check back while writing it.

    :param resources_path: path to the csv file
    :return: dataframe in the same format as returned by parse_resource_file
    """
    return (
        pd.read_csv(resources_path)
        .astype({"time": "datetime64[ns]"})
        .set_index("time")
        .rename({"cpu_cores": "n_cpus", "disk_write": "disk_written"}, axis=1)
        .assign(
            memory=lambda df: df.memory / 1000,
            gpu_memory=lambda df: df.gpu_memory / 1000,
        )
    )


def load_e7_resources_and_timings(path: Path, *, gpu: bool):
    """Identify relevant files in the directories and load data from them.

    :param path: Directory with 'No-GPU' and 'GPU' directories
    :param gpu: Inidicator which of the two options should be used
    """
    base_path = path / "GPU" if gpu else path / "No-GPU"
    recon_logfiles = [
        file
        for file in os.listdir(base_path)
        if file.startswith("log_e7_recon") and not "transformed" in file
    ]
    histo_logfiles = [
        file
        for file in os.listdir(base_path)
        if file.startswith("log_HistogramReplay") and not "transformed" in file
    ]

    assert len(recon_logfiles) == 1
    assert len(histo_logfiles) == 1

    histo_resources_path = base_path / "resources_HistogramReplay_sino_frames.csv"
    recon_resources_path = base_path / "resources_e7_recon_recon.csv"

    histo_logpath = base_path / histo_logfiles.pop()
    recon_logpath = base_path / recon_logfiles.pop()

    transf_histo_logpath = Path(f"{str(histo_logpath)[:-4]}_transformed.txt")
    transf_recon_logpath = Path(f"{str(recon_logpath)[:-4]}_transformed.txt")

    fix_e7_log_column_lengths(recon_logpath, transf_recon_logpath)
    fix_e7_log_column_lengths(histo_logpath, transf_histo_logpath)

    histo_timings = load_e7_histo_timings(transf_histo_logpath)
    recon_timings = load_e7_recon_timings(transf_recon_logpath)

    histo_resource_data = parse_e7_resource_file(histo_resources_path)
    recon_resource_data = parse_e7_resource_file(recon_resources_path)

    return histo_resource_data, histo_timings, recon_resource_data, recon_timings
