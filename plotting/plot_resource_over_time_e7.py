from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .loading import load_e7_resources_and_timings

histo_resources, histo_timings, recon_resources, recon_timings = (
    load_e7_resources_and_timings(Path("results/JSRecon"), gpu=True)
)

mask = (
    recon_resources.index.values[:, None] >= recon_timings[("scatter", "start")].values
) & (recon_resources.index.values[:, None] <= recon_timings[("frame", "end")].values)

ram = recon_resources.loc[mask.any(axis=1), ["memory"]]
mask = mask[mask.any(axis=1)]
ram["frame_nr"] = mask.argmax(axis=1)

mean_ram = ram.groupby("frame_nr").mean()

rate, intercept = np.polyfit(mean_ram.index.values, mean_ram["memory"], 1)

plt.plot(mean_ram.index, mean_ram["memory"])

plt.show()
