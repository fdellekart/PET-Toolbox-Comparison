from pathlib import Path

import pandas as pd

from plotting.loading import (
    prepare_for_single_frame_plot,
    load_e7_resources_and_timings,
)
from plotting.plot import plot_cpu_ram, plot_disk, plot_gpu

FRAME_NR = 80

histo_resource_data, histo_timings, recon_resource_data, recon_timings = (
    load_e7_resources_and_timings(Path("results/JSRecon"), gpu=True)
)

recon_frame_data, recon_frame_timings = prepare_for_single_frame_plot(
    recon_resource_data, recon_timings, FRAME_NR
)
histo_frame_data, histo_frame_timings = prepare_for_single_frame_plot(
    histo_resource_data, histo_timings, FRAME_NR
)

histo_frame_timings.index = pd.MultiIndex.from_product(
    (("histograming",), ("start", "end"))
)
recon_frame_timings = recon_frame_timings + histo_frame_timings.max()
recon_frame_data.index = recon_frame_data.index + histo_frame_timings.max()

frame_data = pd.concat((histo_frame_data, recon_frame_data))
frame_timings = pd.concat((histo_frame_timings, recon_frame_timings))

vert_line_pos = (
    histo_frame_timings[("histograming", "end")] + recon_frame_data.index.min()
) / 2

plot_disk(frame_data, frame_timings, "disk.png", vert_line_pos)
plot_gpu(frame_data, frame_timings, "gpu.png", vert_line_pos)
plot_cpu_ram(frame_data, frame_timings, "cpu_ram.png", vert_line_pos)
