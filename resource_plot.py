import json
from pathlib import Path

from plotting.loading import (
    parse_timings,
    parse_resources_file,
    prepare_for_single_frame_plot,
)
from plotting.plot import plot_cpu_ram, plot_gpu, plot_disk

TOOLBOX_SUPPORTS_GPU = {"SIRF-STIR": False, "NiftyPET": True}
TOOLBOX = "SIRF-STIR"
RUNDIR = Path("results")
FRAME_NR = 25
PLOT_PATH_TEMPLATE = "results/plots/{toolbox}_{resource_type}_frame{frame_nr}.png"
get_plotpath = lambda *args: Path(
    PLOT_PATH_TEMPLATE.format(toolbox=args[0], resource_type=args[1], frame_nr=args[2])
)

resource_file = RUNDIR / TOOLBOX / "resources.csv"
metadata_file = RUNDIR / TOOLBOX / "metadata.json"

with open(metadata_file) as f:
    metadata = json.load(f)

timings = parse_timings(metadata)

resource_data = parse_resources_file(resource_file)
resource_data, frame_timings = prepare_for_single_frame_plot(
    resource_data, timings, FRAME_NR
)

plot_disk(resource_data, frame_timings, get_plotpath(TOOLBOX, "disk", FRAME_NR))
plot_cpu_ram(resource_data, frame_timings, get_plotpath(TOOLBOX, "cup&ram", FRAME_NR))
if TOOLBOX_SUPPORTS_GPU[TOOLBOX]:
    plot_gpu(resource_data, frame_timings, get_plotpath(TOOLBOX, "gpu", FRAME_NR))
