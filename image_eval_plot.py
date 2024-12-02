import json

import matplotlib as mpl
import matplotlib.pyplot as plt


plt.rcParams.update({"font.size": 15})

TOOLBOXES = ["NiftyPET", "SIRF-STIR"]
datafiles = {toolbox: f"results/{toolbox}/evaluation.json" for toolbox in TOOLBOXES}
datafiles["e7-tools"] = "results/JSRecon/No-GPU/evaluation.json"

snrs = []
cnrs = []

for toolbox, datafile in datafiles.items():
    with open(datafile) as f:
        eval_data = json.load(f)

    snrs.append(list(eval_data[75]["snr_per_region"].values()))
    cnrs.append(list(eval_data[75]["cnr_per_region"].values()))

plt.figure(figsize=(7, 5), dpi=300)
plt.ylabel("SNR")
plt.boxplot(snrs, tick_labels=list(datafiles.keys()))
plt.tight_layout()
plt.savefig("SNR.png")
plt.close()

plt.ylabel("CNR")
plt.boxplot(cnrs, tick_labels=list(datafiles.keys()))
plt.tight_layout()
plt.show()
