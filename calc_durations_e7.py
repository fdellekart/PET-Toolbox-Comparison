"""Script to caculate the total durations of substeps in
the reconstruction and there shares of the total time.

For e7-tools data
"""

from pathlib import Path

from plotting.loading import load_e7_resources_and_timings

histo_resources, histo_timings, recon_resources, recon_timings = (
    load_e7_resources_and_timings(Path("results/JSRecon"), gpu=False)
)

histo_start = histo_resources.index[0]
histo_end = histo_resources.index[-1]
recon_start = recon_resources.index[0]
recon_end = recon_resources.index[-1]

total_duration = (histo_end - histo_start) + (recon_end - recon_start)
histo_duration = (
    histo_timings[("frame", "end")] - histo_timings[("frame", "start")]
).sum()
histo_perc = (histo_duration / total_duration) * 100
scatter_duration = (
    recon_timings[("scatter", "end")] - recon_timings[("scatter", "start")]
).sum()
scatter_perc = (scatter_duration / total_duration) * 100
recon_duration = (
    recon_timings[("recon", "end")] - recon_timings[("recon", "start")]
).sum()
recon_perc = (recon_duration / total_duration) * 100
unassigned_duration = (
    total_duration - histo_duration - scatter_duration - recon_duration
)
unassigned_perc = 100 - histo_perc - scatter_perc - recon_perc

print()
