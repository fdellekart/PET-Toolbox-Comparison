from pathlib import Path

import pandas as pd

from plotting.loading import (
    load_e7_resources_and_timings,
)
from plotting.plot import plot_e7_frame

FRAME_NR = 80
PLOT_GPU = True

timing_and_resource_info = load_e7_resources_and_timings(
    Path("results/JSRecon"), gpu=PLOT_GPU
)
plot_e7_frame(
    *timing_and_resource_info, FRAME_NR, Path("./results/plots"), gpu=PLOT_GPU
)
