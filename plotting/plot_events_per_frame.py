import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 15})

data = pd.read_csv("results/events_per_frame.csv")

fig, ax = plt.subplots(1, 1, figsize=(7, 5), dpi=300)

ax.plot(data["frame"], data["prompts"], label="Prompts")
ax.plot(data["frame"], data["delayeds"], label="Delayeds")

ax.set_xlabel("Frame Nr.")
ax.set_ylabel("Number of events per frame")

fig.legend(loc="lower center", ncols=3, frameon=False)
fig.tight_layout(rect=[0, 0.1, 1, 1])
fig.savefig("events.png")
