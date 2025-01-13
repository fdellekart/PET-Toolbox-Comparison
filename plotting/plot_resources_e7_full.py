from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from .loading import load_e7_resources_and_timings

histo_resources, _, recon_resources, _ = load_e7_resources_and_timings(
    Path("./results/JSRecon-HighPower"), gpu=True
)
timediff = recon_resources.index.min() - histo_resources.index.max()
histo_resources.index = histo_resources.index + timediff
resources = pd.concat([histo_resources, recon_resources])
resources.index = (resources.index - resources.index.min()).seconds / 60

fig: plt.Figure
ax_cpu: plt.Axes
ax_mem: plt.Axes

fig, (ax_cpu, ax_mem) = plt.subplots(2, 1, figsize=(7, 5), dpi=300, sharex=True)
ax_cpu.plot(resources.index, resources["n_cpus"])
ax_mem.plot(resources.index, resources["memory"])

ax_cpu.set_ylabel("CPU util. [$n_{cores}$]")
ax_mem.set_ylabel("Memory usage [GB]")
ax_mem.set_xlabel("Time [min]")

plt.tight_layout()
plt.savefig("HP-GPU.png")
