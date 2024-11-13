from pathlib import Path

from tqdm import tqdm

from plotting.loading import (
    load_resources_and_timings,
    prepare_for_single_frame_plot,
    load_e7_resources_and_timings,
)
from plotting.plot import plot_frame, plot_e7_frame

RUNDIR = Path("results")
TOOLBOXES = {"SIRF-STIR", "NiftyPET"}
TOOLBOX_SUPPORTS_GPU = {"SIRF-STIR": False, "NiftyPET": True}

for frame_idx in tqdm(range(106)):
    for toolbox in TOOLBOXES:
        timing_and_resources = load_resources_and_timings(RUNDIR / toolbox)
        frame_timing_and_resource = prepare_for_single_frame_plot(
            *timing_and_resources, frame_idx
        )
        plot_frame(
            *frame_timing_and_resource,
            frame_nr=frame_idx,
            target_dir=Path(f"./results/plots/{toolbox}"),
            gpu=TOOLBOX_SUPPORTS_GPU[toolbox],
        )

    timing_and_resources = load_e7_resources_and_timings(
        Path("results/JSRecon"), gpu=True
    )
    plot_e7_frame(
        *timing_and_resources, frame_idx, Path("./results/plots/e7-tools"), gpu=True
    )

    timing_and_resources = load_e7_resources_and_timings(
        Path("results/JSRecon"), gpu=False
    )
    plot_e7_frame(
        *timing_and_resources, frame_idx, Path("./results/plots/e7-tools"), gpu=False
    )
