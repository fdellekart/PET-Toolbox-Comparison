import json
import copy

import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({"font.size": 15})

TOOLBOXES = ["NiftyPET", "SIRF-STIR"]
datafiles = {toolbox: f"results/{toolbox}/evaluation.json" for toolbox in TOOLBOXES}
datafiles["e7-tools"] = "results/JSRecon/No-GPU/evaluation.json"
datafiles["SIRF"] = datafiles["SIRF-STIR"]
datafiles.pop("SIRF-STIR")

ORDER = ["SIRF", "NiftyPET", "e7-tools"]


data = []
snrs = []
cnrs = []

fig, ax = plt.subplots(1, 1, figsize=(7, 5), dpi=300)

for toolbox in ORDER:
    datafile = datafiles[toolbox]
    with open(datafile) as f:
        eval_data = json.load(f)
        data.append(copy.deepcopy(eval_data))

    snrs = np.array(
        [list(frame_vals["snr_per_region"].values()) for frame_vals in eval_data]
    )

    cnrs.append(list(eval_data[75]["cnr_per_region"].values()))

    means = snrs.mean(axis=1)
    std = snrs.std(axis=1)
    upper_bound = means + std
    lower_bound = means - std

    frame_nr = np.arange(len(means))
    if toolbox == "NiftyPET":
        frame_nr += 10

    ax.plot(frame_nr, means, label=toolbox)
    ax.fill_between(frame_nr, lower_bound, upper_bound, alpha=0.2)

ax.set_xlabel("Frame Nr.")
ax.set_ylabel("SNR")
fig.legend(loc="lower center", ncols=3, frameon=False)
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.savefig("image.png")
