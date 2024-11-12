import pandas as pd

from plotting.loading import (
    fix_e7_log_column_lengths,
    load_e7_recon_timings,
    load_e7_histo_timings,
    prepare_for_single_frame_plot,
    parse_e7_resource_file,
)
from plotting.plot import plot_cpu_ram, plot_disk, plot_gpu

recon_logpath = "results/JSRecon/No-GPU/log_e7_recon_25.txt"
histo_logpath = "results/JSRecon/No-GPU/log_HistogramReplay_25.txt"

transf_recon_logpath = f"{recon_logpath[:-3]}_transformed.txt"
transf_histo_logpath = f"{histo_logpath[:-3]}_transformed.txt"

recon_resources_path = "results/JSRecon/No-GPU/resources_e7_recon_recon.csv"
histo_resources_path = (
    "results/JSRecon/No-GPU/resources_HistogramReplay_sino_frames.csv"
)

START_OF_MSG_COL_IDX = 39
FRAME_NR = 80

fix_e7_log_column_lengths(recon_logpath, transf_recon_logpath)
fix_e7_log_column_lengths(histo_logpath, transf_histo_logpath)

recon_timings = load_e7_recon_timings(transf_recon_logpath)
histo_timings = load_e7_histo_timings(transf_histo_logpath)

recon_resource_data = parse_e7_resource_file(recon_resources_path)
histo_resource_data = parse_e7_resource_file(histo_resources_path)

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
