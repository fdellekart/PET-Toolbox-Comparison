"""Script to caculate the total durations of substeps in
the reconstruction and there shares of the total time.

For non e7-tools data
"""

from pathlib import Path

from plotting.loading import load_resources_and_timings

resources, timings = load_resources_and_timings(Path("results/SIRF-STIR"))

start = resources.index[0]
end = resources.index[-1]

total_duration = end - start
histo_duration = (
    timings[("histograming", "end")] - timings[("histograming", "start")]
).sum()
randoms_duration = (timings[("randoms", "end")] - timings[("randoms", "start")]).sum()
histo_duration = histo_duration + randoms_duration
histo_perc = (histo_duration / total_duration) * 100

is_scatter_start = [
    col[0].startswith("scatter") and col[1] == "start" for col in timings.columns
]
is_scatter_end = [
    col[0].startswith("scatter") and col[1] == "end" for col in timings.columns
]

scatter_ends = timings.loc[:, is_scatter_end]
scatter_starts = timings.loc[:, is_scatter_start]
scatter_ends.columns = scatter_ends.columns.droplevel(level=1)
scatter_starts.columns = scatter_starts.columns.droplevel(level=1)
scatter_duration = (scatter_ends - scatter_starts).sum().sum()
scatter_perc = (scatter_duration / total_duration) * 100

is_recon_start = [
    col[0].startswith("recon") and col[1] == "start" for col in timings.columns
]
is_recon_end = [
    col[0].startswith("recon") and col[1] == "end" for col in timings.columns
]

recon_ends = timings.loc[:, is_recon_end]
recon_starts = timings.loc[:, is_recon_start]
recon_ends.columns = recon_ends.columns.droplevel(level=1)
recon_starts.columns = recon_starts.columns.droplevel(level=1)
recon_duration = (recon_ends - recon_starts).sum().sum()
recon_perc = (recon_duration / total_duration) * 100

unassigned_duration = (
    total_duration - histo_duration - scatter_duration - recon_duration
)
unassigned_perc = (unassigned_duration / total_duration) * 100
