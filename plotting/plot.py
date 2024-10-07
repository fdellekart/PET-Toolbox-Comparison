import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from plotting.utils import add_blocks_to_ax, MyFormatter


def plot_cpu_ram(resource_data: pd.DataFrame, frame_timings: pd.Series) -> None:
    fig, (cpu_ax, mem_ax) = plt.subplots(1, 2)

    cpu_ax.set_title("Number of used CPU cores")
    mem_ax.set_title("RAM usage in GB")

    cpu_ax.plot(resource_data.index, resource_data["n_cpus"])
    mem_ax.plot(resource_data.index, resource_data["memory"])

    cpu_ax.xaxis.set_major_formatter(MyFormatter())
    mem_ax.xaxis.set_major_formatter(MyFormatter())

    cpu_ax.set_ylim(bottom=0)
    mem_ax.set_ylim(bottom=0)

    cpu_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    cpu_ax.set_xticklabels(cpu_ax.get_xticklabels(), rotation=50)

    mem_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    mem_ax.set_xticklabels(cpu_ax.get_xticklabels(), rotation=50)

    add_blocks_to_ax(cpu_ax, frame_timings)
    add_blocks_to_ax(mem_ax, frame_timings)

    cpu_ax.legend()

    plt.tight_layout()
    plt.show()


def plot_gpu(resource_data: pd.DataFrame, frame_timings: pd.Series) -> None:
    fig, (gpu_util_ax, gpu_mem_ax) = plt.subplots(1, 2)

    gpu_util_ax.set_title("GPU utilization in %")
    gpu_mem_ax.set_title("GPU memory usage in GB")

    gpu_util_ax.plot(resource_data.index, resource_data["gpu_util"])
    gpu_mem_ax.plot(resource_data.index, resource_data["gpu_memory"])

    gpu_util_ax.xaxis.set_major_formatter(MyFormatter())
    gpu_mem_ax.xaxis.set_major_formatter(MyFormatter())

    gpu_util_ax.set_ylim(bottom=0)
    gpu_mem_ax.set_ylim(bottom=0)

    gpu_util_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    gpu_util_ax.set_xticklabels(gpu_util_ax.get_xticklabels(), rotation=50)

    gpu_mem_ax.set_xticks(np.arange(0, resource_data.index.max(), 60))
    gpu_mem_ax.set_xticklabels(gpu_mem_ax.get_xticklabels(), rotation=50)

    add_blocks_to_ax(gpu_util_ax, frame_timings)
    add_blocks_to_ax(gpu_mem_ax, frame_timings)

    gpu_util_ax.legend()

    plt.tight_layout()
    plt.show()
