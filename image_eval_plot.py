import json

import matplotlib.pyplot as plt


TOOLBOXES = ["NiftyPET", "SIRF-STIR"]
datafiles = {
    toolbox: f"results/2024-10-04-16-24-afbd5f5/{toolbox}/evaluation.json"
    for toolbox in TOOLBOXES
}
datafiles["JSRecon"] = "results/JSRecon/evaluation.json"

snrs = []

for toolbox, datafile in datafiles.items():
    with open(datafile) as f:
        eval_data = json.load(f)

    snrs.append(list(eval_data["snr_per_region"].values()))


plt.boxplot(snrs, tick_labels=list(datafiles.keys()))
plt.show()
