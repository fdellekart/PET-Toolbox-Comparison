import os

import pandas as pd

filepath = "results/JSRecon/GPU/log_e7_recon_23.txt"
transformed_filepath = f"{filepath[:-3]}_transformed.txt"
START_OF_MSG_COL_IDX = 39

FRAME_NR = 25

if not os.path.exists(transformed_filepath):
    with open(filepath, "r") as f:
        next(f)  # Drop header
        log_lines = f.readlines()

    max_msg_col_length = max(len(line) for line in log_lines)

    with open(transformed_filepath, "w") as f:
        f.write(f"{max_msg_col_length}\n")
        for original_line in log_lines:
            msg_col_length = len(original_line) - START_OF_MSG_COL_IDX
            new_line = (
                original_line[:-1] + " " * (max_msg_col_length - msg_col_length) + "\n"
            )
            f.write(new_line)

with open(transformed_filepath, "r") as f:
    max_msg_col_length = int(f.readline()[:-1])

data = pd.read_fwf(
    transformed_filepath, colspecs=[(0, 1), (2, 25), (38, max_msg_col_length)]
)
data.columns = ["msg_type", "time", "msg"]
data["time"] = pd.to_datetime(data["time"])
data.set_index("time", inplace=True)
data["msg"] = data["msg"].str.strip()
cond_start = data["msg"].str.startswith("axis table=4084").fillna(False)
cond_end = data["msg"].str.startswith("finished calculation of image").fillna(False)

frame_starts = data[cond_start].index
frame_ends = data[cond_end].index

frame_timings = pd.DataFrame(data={"start": frame_starts, "end": frame_ends})
