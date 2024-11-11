from plotting.loading import (
    fix_e7_log_column_lengths,
    load_e7_frame_timings,
    prepare_for_single_frame_plot,
    parse_e7_resource_file,
)
from plotting.plot import plot_cpu_ram

logpath = "results/JSRecon/GPU/log_e7_recon_23.txt"
transformed_logpath = f"{logpath[:-3]}_transformed.txt"
resources_path = "results/JSRecon/GPU/resources_e7_recon_recon.csv"

START_OF_MSG_COL_IDX = 39
FRAME_NR = 25

fix_e7_log_column_lengths(logpath, transformed_logpath)
frame_timings = load_e7_frame_timings(transformed_logpath)

resource_data = parse_e7_resource_file(resources_path)
frame_data, timings = prepare_for_single_frame_plot(
    resource_data, frame_timings, FRAME_NR
)

plot_cpu_ram(frame_data, timings, "plot.png")
