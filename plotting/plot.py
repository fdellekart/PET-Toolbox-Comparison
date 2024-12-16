from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from plotting.utils import add_blocks_to_ax, MyFormatter
from plotting.loading import prepare_for_single_frame_plot


def plot_frame(
    resources: pd.DataFrame,
    timings: pd.Series,
    frame_nr: int,
    target_dir: Path,
    gpu: bool,
):
    """Plot disk, cpu&ram and, if gpu==True, gpu."""
    plot_disk(resources, timings, target_dir / f"disk_frame{frame_nr}.png")
    plot_cpu_ram(resources, timings, target_dir / f"cpu&ram_frame{frame_nr}.png")
    if gpu:
        plot_gpu(resources, timings, target_dir / f"gpu_frame{frame_nr}.png")


def plot_cpu_ram(
    resource_data: pd.DataFrame,
    frame_timings: pd.Series,
    target_file: Optional[Path] = None,
    vertical_line_pos: Optional[int] = None,
) -> None:
    fig: plt.Figure
    cpu_ax: plt.Axes
    mem_ax: plt.Axes

    fig, (cpu_ax, mem_ax) = plt.subplots(2, 1, figsize=(7, 5), dpi=300, sharex=True)

    cpu_ax.set_ylabel("CPU utilization [$n_{cores}$]")
    mem_ax.set_ylabel("Memory usage [GB]")
    mem_ax.set_xlabel("Time [min]")
    cpu_ax.set_xlim(0, resource_data.index.max())
    mem_ax.set_xlim(0, resource_data.index.max())

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
    fig: plt.Figure
    gpu_util_ax: plt.Axes
    gpu_mem_ax: plt.Axes

    fig, (gpu_util_ax, gpu_mem_ax) = plt.subplots(
        2, 1, figsize=(7, 5), dpi=300, sharex=True
    )

    gpu_util_ax.set_ylabel("GPU utilization [%]")
    gpu_mem_ax.set_ylabel("GPU memory usage [GB]")
    gpu_mem_ax.set_xlabel("Time [min]")
    gpu_util_ax.set_xlim(0, resource_data.index.max())
    gpu_mem_ax.set_xlim(0, resource_data.index.max())

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
    fig: plt.Figure
    read_ax: plt.Axes
    write_ax: plt.Axes

    fig, (read_ax, write_ax) = plt.subplots(2, 1, figsize=(7, 5), dpi=300, sharex=True)

    read_ax.set_title("Data read from disk")
    write_ax.set_title("Data written to disk")
    read_ax.set_ylabel("MB/s")
    write_ax.set_ylabel("MB/s")
    write_ax.set_xlabel("Time [min]")
    read_ax.set_xlim(0, resource_data.index.max())
    write_ax.set_xlim(0, resource_data.index.max())

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


def plot_e7_frame(
    histo_resource_data: pd.DataFrame,
    histo_timings: pd.DataFrame,
    recon_resource_data: pd.DataFrame,
    recon_timings: pd.DataFrame,
    frame_nr: int,
    target_dir: Path,
    gpu: bool,
):
    """Plot all plots for the single frame and save them to target dir."""
    recon_frame_data, recon_frame_timings = prepare_for_single_frame_plot(
        recon_resource_data, recon_timings, frame_nr
    )
    histo_frame_data, histo_frame_timings = prepare_for_single_frame_plot(
        histo_resource_data, histo_timings, frame_nr
    )

    histo_frame_timings.index = pd.MultiIndex.from_product(
        (("histograming",), ("start", "end"))
    )
    recon_frame_timings = recon_frame_timings + histo_frame_timings.max()
    recon_frame_data.index = recon_frame_data.index + histo_frame_timings.max()

    frame_data = pd.concat((histo_frame_data, recon_frame_data))
    frame_timings = pd.concat((histo_frame_timings, recon_frame_timings))

    vert_line_pos = (
        histo_frame_timings[("histograming", "end")] + recon_frame_data.index.min()
    ) / 2

    plot_disk(
        frame_data,
        frame_timings,
        target_dir / f"e7-tools{'-gpu' if gpu else ''}_disk_frame{frame_nr}.png",
        vert_line_pos,
    )
    plot_cpu_ram(
        frame_data,
        frame_timings,
        target_dir / f"e7-tools{'-gpu' if gpu else ''}_cpu&ram_frame{frame_nr}.png",
        vert_line_pos,
    )
    if gpu:
        plot_gpu(
            frame_data,
            frame_timings,
            target_dir / f"e7-tools{'-gpu' if gpu else ''}_gpu_frame{frame_nr}.png",
            vert_line_pos,
        )
