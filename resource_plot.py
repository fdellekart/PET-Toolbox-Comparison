import json
from pathlib import Path

from plotting.loading import (
    parse_timings,
    parse_resources_file,
    prepare_for_single_frame_plot,
)
from plotting.plot import plot_cpu_ram, plot_gpu

TOOLBOX_SUPPORTS_GPU = {"SIRF-STIR": False, "NiftyPET": True}
TOOLBOX = "SIRF-STIR"
RUNDIR = Path("results/2024-10-04-16-24-afbd5f5")

resource_file = RUNDIR / TOOLBOX / "resources.csv"
metadata_file = RUNDIR / TOOLBOX / "metadata.json"

with open(metadata_file) as f:
    metadata = json.load(f)

timings = parse_timings(metadata)
frame_timings = timings.loc[1, :]

resource_data = parse_resources_file(resource_file)
resource_data, frame_timings = prepare_for_single_frame_plot(
    resource_data, frame_timings
)

plot_cpu_ram(resource_data, frame_timings)
if TOOLBOX_SUPPORTS_GPU[TOOLBOX]:
    plot_gpu(resource_data, frame_timings)
