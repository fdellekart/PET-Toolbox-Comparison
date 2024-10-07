import json

import matplotlib.pyplot as plt


TOOLBOXES = ["NiftyPET", "SIRF-STIR"]

snrs = []

for toolbox in TOOLBOXES:
    datafile = f"results/2024-10-04-16-24-afbd5f5/{toolbox}/evaluation.json"

    with open(datafile) as f:
        eval_data = json.load(f)

    snrs.append(list(eval_data["snr_per_region"].values()))


plt.boxplot(snrs, tick_labels=TOOLBOXES)
plt.show()
