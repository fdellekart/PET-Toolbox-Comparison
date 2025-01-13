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

timing_and_resources = {
    toolbox: load_resources_and_timings(RUNDIR / toolbox) for toolbox in TOOLBOXES
}

for frame_idx in tqdm(range(106), "Processing generic toolbox frames"):
    for toolbox in TOOLBOXES:
        # NiftyPET only starts at frame 10 because it fails on lack of events before
        if toolbox == "NiftyPET" and frame_idx < 10:
            continue

        frame_timing_and_resource = prepare_for_single_frame_plot(
            *timing_and_resources[toolbox],
            frame_idx - 10 if toolbox == "NiftyPET" else frame_idx,
        )
        plot_frame(
            *frame_timing_and_resource,
            frame_nr=frame_idx,
            target_dir=Path(f"./results/plots/{toolbox}"),
            gpu=TOOLBOX_SUPPORTS_GPU[toolbox],
        )

timing_and_resources_gpu = load_e7_resources_and_timings(
    Path("results/JSRecon"), gpu=True
)
timing_and_resources_nogpu = load_e7_resources_and_timings(
    Path("results/JSRecon"), gpu=False
)

for frame_idx in tqdm(range(106), "Processing e7 frames"):
    plot_e7_frame(
        *timing_and_resources_gpu, frame_idx, Path("./results/plots/e7-tools"), gpu=True
    )
    plot_e7_frame(
        *timing_and_resources_nogpu,
        frame_idx,
        Path("./results/plots/e7-tools"),
        gpu=False,
    )
