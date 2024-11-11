import pandas as pd

from plotting.loading import fix_e7_log_column_lengths, load_e7_frame_timings

logpath = "results/JSRecon/GPU/log_e7_recon_23.txt"
transformed_logpath = f"{logpath[:-3]}_transformed.txt"
START_OF_MSG_COL_IDX = 39
FRAME_NR = 25

fix_e7_log_column_lengths(logpath, transformed_logpath)
frame_timings = load_e7_frame_timings(transformed_logpath)
