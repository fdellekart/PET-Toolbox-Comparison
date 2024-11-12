from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from plotting.utils import add_blocks_to_ax, MyFormatter


def plot_cpu_ram(
    resource_data: pd.DataFrame,
    frame_timings: pd.Series,
    target_file: Optional[Path] = None,
    vertical_line_pos: Optional[int] = None,
) -> None:
    fig, (cpu_ax, mem_ax) = plt.subplots(2, 1, figsize=(7, 5), dpi=300, sharex=True)

    cpu_ax.set_ylabel("CPU utilization [$n_{cores}$]")
    mem_ax.set_ylabel("Memory usage [GB]")
    mem_ax.set_xlabel("Time [min]")

    if resource_data["n_cpus"].max() < 1.05:
        cpu_ax.set_ylim(0, 1.05)

    cpu_ax.plot(resource_data.index, resource_data["n_cpus"])
    mem_ax.plot(resource_data.index, resource_data["memory"])

    if vertical_line_pos is not None:
        cpu_ax.axvline(vertical_line_pos, linestyle="--", color="black", linewidth=1)
        mem_ax.axvline(vertical_line_pos, linestyle="--", color="black", linewidth=1)

    cpu_ax.xaxis.set_major_formatter(MyFormatter())

    cpu_ax.set_ylim(bottom=0)
    mem_ax.set_ylim(bottom=0)

    cpu_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    mem_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))

    add_blocks_to_ax(cpu_ax, frame_timings)
    add_blocks_to_ax(mem_ax, frame_timings)

    handles, labels = cpu_ax.get_legend_handles_labels()

    if len(handles) >= 2:
        handles[-2], handles[-1] = handles[-1], handles[-2]
        labels[-2], labels[-1] = labels[-1], labels[-2]

    fig.legend(handles, labels, ncols=4, loc="lower center", frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if target_file is None:
        plt.show()
    else:
        plt.savefig(target_file)
    plt.close()


def plot_gpu(
    resource_data: pd.DataFrame,
    frame_timings: pd.Series,
    target_file: Optional[Path] = None,
    vertical_line_pos: Optional[int] = None,
) -> None:
    fig, (gpu_util_ax, gpu_mem_ax) = plt.subplots(
        2, 1, figsize=(7, 5), dpi=300, sharex=True
    )

    gpu_util_ax.set_ylabel("GPU utilization [%]")
    gpu_mem_ax.set_ylabel("GPU memory usage [GB]")
    gpu_mem_ax.set_xlabel("Time [min]")

    gpu_util_ax.plot(resource_data.index, resource_data["gpu_util"])
    gpu_mem_ax.plot(resource_data.index, resource_data["gpu_memory"])

    if vertical_line_pos is not None:
        gpu_util_ax.axvline(
            vertical_line_pos, linestyle="--", color="black", linewidth=1
        )
        gpu_mem_ax.axvline(
            vertical_line_pos, linestyle="--", color="black", linewidth=1
        )

    gpu_mem_ax.xaxis.set_major_formatter(MyFormatter())

    gpu_util_ax.set_ylim(bottom=0)
    gpu_mem_ax.set_ylim(bottom=0)

    gpu_util_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    gpu_mem_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))

    add_blocks_to_ax(gpu_util_ax, frame_timings)
    add_blocks_to_ax(gpu_mem_ax, frame_timings)

    handles, labels = gpu_util_ax.get_legend_handles_labels()
    if len(handles) >= 2:
        handles[-2], handles[-1] = handles[-1], handles[-2]
        labels[-2], labels[-1] = labels[-1], labels[-2]

    fig.legend(handles, labels, ncols=4, loc="lower center", frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if target_file is None:
        plt.show()
    else:
        plt.savefig(target_file)
    plt.close()


def plot_disk(
    resource_data: pd.DataFrame,
    frame_timings: pd.Series,
    target_file: Optional[Path] = None,
    vertical_line_pos: Optional[int] = None,
) -> None:
    fig, (read_ax, write_ax) = plt.subplots(2, 1, figsize=(7, 5), dpi=300, sharex=True)

    read_ax.set_title("Data read from disk")
    write_ax.set_title("Data written to disk")
    read_ax.set_ylabel("MB/s")
    write_ax.set_ylabel("MB/s")
    write_ax.set_xlabel("Time [min]")

    read_ax.plot(resource_data.index, resource_data["disk_read"])
    write_ax.plot(resource_data.index, resource_data["disk_written"])

    if vertical_line_pos is not None:
        read_ax.axvline(vertical_line_pos, linestyle="--", color="black", linewidth=1)
        write_ax.axvline(vertical_line_pos, linestyle="--", color="black", linewidth=1)

    read_ax.xaxis.set_major_formatter(MyFormatter())

    read_ax.set_ylim(bottom=0)
    write_ax.set_ylim(bottom=0)

    read_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    write_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))

    add_blocks_to_ax(read_ax, frame_timings)
    add_blocks_to_ax(write_ax, frame_timings)

    handles, labels = read_ax.get_legend_handles_labels()
    if len(handles) >= 2:
        handles[-2], handles[-1] = handles[-1], handles[-2]
        labels[-2], labels[-1] = labels[-1], labels[-2]

    fig.legend(handles, labels, ncols=4, loc="lower center", frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if target_file is None:
        plt.show()
    else:
        plt.savefig(target_file)
    plt.close()
