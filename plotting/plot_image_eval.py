import json
import copy

import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({"font.size": 15})

TOOLBOXES = ["NiftyPET"]
datafiles = {toolbox: f"results/{toolbox}/evaluation.json" for toolbox in TOOLBOXES}
datafiles["e7-tools"] = "results/JSRecon/No-GPU/evaluation.json"

ORDER = ["e7-tools", "NiftyPET"]


data = []
snrs = []
cnrs = []

fig_snr, ax_snr = plt.subplots(1, 1, figsize=(7, 5), dpi=300)
fig_cnr, ax_cnr = plt.subplots(1, 1, figsize=(7, 5), dpi=300)

for toolbox in ORDER:
    datafile = datafiles[toolbox]
    with open(datafile) as f:
        eval_data = json.load(f)
        data.append(copy.deepcopy(eval_data))

    snrs = np.array(
        [list(frame_vals["snr_per_region"].values()) for frame_vals in eval_data]
    )
    cnrs = np.array(
        [list(frame_vals["cnr_per_region"].values()) for frame_vals in eval_data]
    )

    snr_means = snrs.mean(axis=1)
    snr_std = snrs.std(axis=1)
    snr_upper_bound = snr_means + snr_std
    snr_lower_bound = snr_means - snr_std

    cnr_means = cnrs.mean(axis=1)
    cnr_means[cnr_means > 100] = 0
    cnr_std = cnrs.std(axis=1)
    cnr_std[cnr_std > 4] = 0
    cnr_upper_bound = cnr_means + cnr_std
    cnr_lower_bound = cnr_means - cnr_std

    frame_nr = np.arange(len(snr_means))
    if toolbox == "NiftyPET":
        frame_nr += 10

    ax_snr.plot(frame_nr, snr_means, label=toolbox)
    ax_snr.fill_between(frame_nr, snr_lower_bound, snr_upper_bound, alpha=0.2)

ax_snr.set_xlabel("Frame Nr.")
ax_cnr.set_xlabel("Frame Nr.")
ax_cnr.set_ylim(0)

ax_snr.set_ylabel("SNR")
ax_cnr.set_ylabel("CNR")

fig_snr.legend(loc="lower center", ncols=3, frameon=False)
fig_cnr.legend(loc="lower center", ncols=3, frameon=False)

fig_snr.tight_layout(rect=[0, 0.1, 1, 1])
fig_cnr.tight_layout(rect=[0, 0.1, 1, 1])

fig_snr.savefig("snr.png")
fig_cnr.savefig("cnr.png")
