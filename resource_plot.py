import json
from pathlib import Path

from plotting.loading import (
    parse_timings,
    parse_resources_file,
    prepare_for_single_frame_plot,
    load_e7_resources_and_timings,
)
from plotting.plot import plot_cpu_ram, plot_gpu, plot_disk, plot_e7_frame

RUNDIR = Path("results")
PLOT_PATH_TEMPLATE = "results/plots/{toolbox}_{resource_type}_frame{frame_nr}.png"
get_plotpath = lambda *args: Path(
    PLOT_PATH_TEMPLATE.format(toolbox=args[0], resource_type=args[1], frame_nr=args[2])
)

TOOLBOXES = {"SIRF-STIR", "NiftyPET"}
TOOLBOX_SUPPORTS_GPU = {"SIRF-STIR": False, "NiftyPET": True}
FRAME_NR = 25

for toolbox in TOOLBOXES:
    resource_file = RUNDIR / toolbox / "resources.csv"
    metadata_file = RUNDIR / toolbox / "metadata.json"

    with open(metadata_file) as f:
        metadata = json.load(f)

    timings = parse_timings(metadata)

    resource_data = parse_resources_file(resource_file)
    resource_data, frame_timings = prepare_for_single_frame_plot(
        resource_data, timings, FRAME_NR
    )

    plot_disk(resource_data, frame_timings, get_plotpath(toolbox, "disk", FRAME_NR))
    plot_cpu_ram(
        resource_data, frame_timings, get_plotpath(toolbox, "cup&ram", FRAME_NR)
    )
    if TOOLBOX_SUPPORTS_GPU[toolbox]:
        plot_gpu(resource_data, frame_timings, get_plotpath(toolbox, "gpu", FRAME_NR))


timing_and_resource_info = load_e7_resources_and_timings(
    Path("results/JSRecon"), gpu=True
)
plot_e7_frame(*timing_and_resource_info, FRAME_NR, Path("./results/plots"), gpu=True)

timing_and_resource_info = load_e7_resources_and_timings(
    Path("results/JSRecon"), gpu=False
)
plot_e7_frame(*timing_and_resource_info, FRAME_NR, Path("./results/plots"), gpu=False)
