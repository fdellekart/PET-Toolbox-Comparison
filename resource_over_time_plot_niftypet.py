from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plotting.loading import load_resources_and_timings

resources, timings = load_resources_and_timings(Path("results/SIRF-STIR"))

mask = (resources.index.values[:, None] >= timings[("frame", "start")].values) & (
    resources.index.values[:, None] <= timings[("frame", "end")].values
)

ram = resources.loc[mask.any(axis=1), ["memory"]]
mask = mask[mask.any(axis=1)]
ram["frame_nr"] = mask.argmax(axis=1)

mean_ram = ram.groupby("frame_nr").mean()
mean_ram = mean_ram.loc[1:, :]

rate, intercept = np.polyfit(mean_ram.index.values, mean_ram["memory"], 1)

plt.plot(mean_ram.index, mean_ram["memory"])
plt.show()

histograming = timings[("histograming", "end")] - timings[("histograming", "start")]
randoms = timings[("randoms", "end")] - timings[("randoms", "start")]
scatter = timings[("scatter", "end")] - timings[("scatter", "start")]
recon = timings[("recon", "end")] - timings[("recon", "start")]

plt.figure(figsize=(7, 5), dpi=300)
plt.plot(histograming.index, histograming.dt.seconds, label="histograming")
plt.plot(randoms.index, randoms.dt.seconds, label="randoms")
plt.ylabel("Time [s]")
plt.xlabel("Frame Nr.")
plt.legend()
plt.tight_layout()
plt.savefig("image.png")
