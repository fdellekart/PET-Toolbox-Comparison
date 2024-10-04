import numpy as np
import pandas as pd


datafile = "./results/2024-10-04-12-01-961a40e/NiftyPET/resources.csv"


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


data = parse_resources_file(datafile)
print()
