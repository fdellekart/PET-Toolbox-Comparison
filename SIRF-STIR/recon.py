import os
import sys
from typing import Tuple, Any
from pathlib import Path

import numpy as np
import nibabel as nib
from sirf.STIR import *
import sirf.Reg as reg

from utils import get_intervals, get_file_with_suffix, ReconMetadata

output_path = Path(f"./output/")

meta = ReconMetadata(os.getenv("GIT_COMMIT_SHORT_SHA"))
meta.start()

TIME_START, TIME_END, TIME_STEP = [int(val) for val in sys.argv[1:]]
meta.add_metadatum("time_start", TIME_START)
meta.add_metadatum("time_end", TIME_END)
meta.add_metadatum("time_step", TIME_STEP)

# Find the path to the data directory
input_data_path = "/home/jovyan/work/recon/input"
outpu_data_path = "/home/jovyan/work/recon/output"

# input files
list_file = get_file_with_suffix(".l.hdr", input_data_path)
norm_file = get_file_with_suffix(".n.hdr", input_data_path)
attn_file = os.path.join(outpu_data_path, "combined_mumap.nii")

# output filename prefixes
SINO_FILE_PREFIX = "sino"

IMAGE_X_SIZE = meta.add_metadatum("image_x_size", 344)
IMAGE_Y_SIZE = meta.add_metadatum("image_y_size", 344)

# Choose a number of subsets.
# For the mMR, best performance requires to not use a multiple of 9 as there are gaps
# in the sinograms, resulting in unbalanced subsets (which isn't ideal for OSEM).
NUM_SUBSETS = meta.add_metadatum("num_subsets", 21)
# (Clinical reconstructions use around 60 subiterations, e.g. 21 subsets, 3 full iterations)
NUM_SUBITERATIONS = meta.add_metadatum("num_subiterations", 60)

NUM_ITERATIONS_SCATTER = meta.add_metadatum("num_iterations_scatter", 3)
NUM_SUBSETS_SCATTER = meta.add_metadatum("num_subsets_scatter", 21)

PRE_SMOOTHING_FWHM = meta.add_metadatum("psf_fwhm", 4)

SPAN = meta.add_metadatum("span", 11)
MAX_RING_DIFF = meta.add_metadatum("max_ring_diff", 60)
VIEW_MASH_FACTOR = meta.add_metadatum("view_mash_factor", 1)

# redirect STIR messages to some files
# you can check these if things go wrong
_ = MessageRedirector("info.txt", "warnings.txt")

template_acq_data = AcquisitionData(
    "Siemens_mMR",
    span=SPAN,
    max_ring_diff=MAX_RING_DIFF,
    view_mash_factor=VIEW_MASH_FACTOR,
)
template_acq_data.write("template.hs")


def make_sinogram(
    list_file: str, time_start: int, time_end: int
) -> Tuple[AcquisitionData, Any]:  # TODO: Check type of randoms
    """Process the listmode data to produce a sinogram for the given time interval

    :param list_filepath: Filepath to listmode data file header in STIR .l.hdr format
        File can be obtained from dcm/bf format with pet_rd_tools nm_extract
    :param time_start: Start of timeframe in seconds from start
    :param time_end: End of timeframe in seconds from start
    :return: Tuple with the sinogram and estimated randoms
    """
    meta.start_block("histograming")

    lm2sino = ListmodeToSinograms()

    lm2sino.set_input(list_file)
    lm2sino.set_output_prefix(SINO_FILE_PREFIX)
    lm2sino.set_template("template.hs")
    lm2sino.set_time_interval(time_start, time_end)

    lm2sino.set_up()
    lm2sino.process()

    meta.end_block("histograming")
    meta.start_block("randoms")

    randoms = lm2sino.estimate_randoms()

    meta.end_block("randoms")

    return lm2sino.get_output(), randoms


def load_attenuation_image(filepath: str, acq_data: AcquisitionData) -> ImageData:
    """Load attenuation image into object and ensure positional alignment.

    :param attenuation_filepath: Mumap .nii filepath with combination of hardware and subject mumap.
        pet_rd_tools nm_mrac2mu can be used to convert MRAC pseudo-CTs to mumap and
        the merge_umaps.py script to combine the result with the hardware mumap
    :param acq_data: Sinogram data from make_sinogram
    :return: ImageData object with the loaded image
    """
    attn_image = ImageData(filepath)
    return attn_image.move_to_scanner_centre(acq_data)


def make_acquisition_sensitivity(
    acq_data: AcquisitionData, norm_filepath: str, attenuation_image: ImageData
) -> Tuple[AcquisitionSensitivityModel, Any]:
    """Combine detector efficiencies calculated from norm
    file and attenuation model into one acquisition
    sensitivity model.

    :param acq_data: Sinogram data from make_sinogram
    :param norm_filepath: filepath to normalization file header in STIR .n.hdr format
    :param attenuation_image: Mumap loaded with get_attenuation_image
    :return: Prepared STIR AcquistionSensitivityModel object
        combining attenuation and detector efficiencies, Attenuation factors
    """
    asm_norm = AcquisitionSensitivityModel(norm_filepath)
    asm_norm.set_up(acq_data)
    det_efficiencies = acq_data.get_uniform_copy(1)
    asm_norm.unnormalise(det_efficiencies)

    attn_acq_model = AcquisitionModelUsingRayTracingMatrix()
    asm_attn = AcquisitionSensitivityModel(attenuation_image, attn_acq_model)
    # converting attenuation into attenuation factors (see previous exercise)
    asm_attn.set_up(acq_data)
    attn_factors = acq_data.get_uniform_copy(1)
    print("applying attenuation (please wait, may take a while)...")
    asm_attn.unnormalise(attn_factors)

    asm_attn = AcquisitionSensitivityModel(attn_factors)
    asm = AcquisitionSensitivityModel(asm_norm, asm_attn)
    asm.set_up(acq_data)

    return asm, attn_factors


def make_scatter_estimate(
    acq_data: AcquisitionData,
    attenuation_image: ImageData,
    randoms: AcquisitionData,
    asm: AcquisitionSensitivityModel,
    attn_factors: Any,
) -> AcquisitionData:
    """Setup and process scatter estimation.

    :param acq_data: Sinogram data from make_sinogram
    :param attenuation_image: The combined object and hardware umap
    :param randoms: Estimated randoms as returned by make_sinogram
    :param asm: acquisition sensitivity as returned by make_acquisition_sensitivity
    :param attn_factors: attenuation factors as returned by make_acquisition_sensitivity
    :return: Estimated scatter sinogram. Currently dividing the output by 1000 because
        the scatter estimation broke the reconstruction and it looked like if the problem
        is with units when comparing them to the randoms. However, this is not 100% sure.
    """
    meta.start_block("scatter")

    se = ScatterEstimator()
    se.set_input(acq_data)
    se.set_attenuation_image(attenuation_image)
    se.set_randoms(randoms)
    se.set_asm(asm)

    acf_factors = attn_factors.get_uniform_copy()
    acf_factors.fill(1 / attn_factors.as_array())

    se.set_attenuation_correction_factors(acf_factors)
    se.set_num_iterations(NUM_ITERATIONS_SCATTER)
    se.set_output_prefix("scatter_estimate")
    se.set_OSEM_num_subsets(NUM_SUBSETS_SCATTER)

    se.set_up()
    se.process()

    meta.end_block("scatter")

    return (
        se.get_output() / 1000
    )  # TODO: find out why this looks so bad. It should be a quite uniform background


def make_acquisiton_model(
    asm: AcquisitionSensitivityModel,
    acq_data: AcquisitionData,
    randoms: AcquisitionData,
    scatter_estimate: AcquisitionData,
    initial_image: ImageData,  # Type sure?
) -> AcquisitionModelUsingRayTracingMatrix:
    """Combine acquistion data, randoms and scatter into an acquisition model.
    Uses acquisition model relying on ray tracing matrix.

    :param asm: Acquisition sensitivity model as returned by make_acquisition_sensitivity
    :param acq_data: Acqisition data as returned by make_sinogram
    :param randoms: Randoms as returned by make_sinogram
    :param scatter_estimate: Scatter estimated as returned by estimage_scatter
    :param initial_image: Initial value for the image to start from
    :return: The set up acquisition model
    """
    acq_model = AcquisitionModelUsingRayTracingMatrix()
    smoother = SeparableGaussianImageFilter()
    smoother.set_fwhms((PRE_SMOOTHING_FWHM, PRE_SMOOTHING_FWHM, PRE_SMOOTHING_FWHM))
    acq_model.set_image_data_processor(smoother)
    acq_model.set_acquisition_sensitivity(asm)
    acq_model.set_background_term(randoms + scatter_estimate)
    acq_model.set_up(acq_data, initial_image)
    return acq_model


def reconstruct(
    acq_data: AcquisitionData,
    acq_model: AcquisitionModelUsingRayTracingMatrix,
    initial_image: ImageData,
) -> AcquisitionData:
    """Setup objective function and reconstructor.
    Process and return the output.

    :param acq_data: Acquisition data returned by make_sinogram
    :param acq_model: Acqisition model returned by make_acquisition_model
    :param initial image: Initial image to start with
    :return: Processed reconstruction
    """
    meta.start_block("recon")

    obj_fun = make_Poisson_loglikelihood(acq_data=acq_data, acq_model=acq_model)
    obj_fun.set_up(initial_image)

    recon = OSMAPOSLReconstructor()

    recon.set_num_subsets(NUM_SUBSETS)
    recon.set_num_subiterations(NUM_SUBITERATIONS)

    recon.set_objective_function(obj_fun)
    recon.set_up(initial_image)
    recon.set_current_estimate(initial_image)
    recon.process()

    meta.end_block("recon")

    return recon.get_output()


def reconstruct_frame(time_start: int, time_end: int, frame_idx: int) -> np.array:
    """Run reconstruction for a single frame.

    :param time_start: Start of frame in seconds from beginning
    :param time_end: End of frame in seconds from beginning
    :param frame_idx: Index of the current frame
    """
    acq_data, randoms = make_sinogram(list_file, time_start, time_end)
    attenuation_image = load_attenuation_image(attn_file, acq_data)
    asm, attn_factors = make_acquisition_sensitivity(
        acq_data, norm_file, attenuation_image
    )
    scatter_estimate = make_scatter_estimate(
        acq_data, attenuation_image, randoms, asm, attn_factors
    )

    initial_image = acq_data.create_uniform_image(1.0, (IMAGE_X_SIZE, IMAGE_Y_SIZE))
    acq_model = make_acquisiton_model(
        asm, acq_data, randoms, scatter_estimate, initial_image
    )

    recon = reconstruct(acq_data, acq_model, initial_image)

    reg.NiftiImageData(recon).write(f"./output/frame_{frame_idx}.nii")

    return recon.as_array()


result = []
intervals = get_intervals(TIME_START, TIME_END, TIME_STEP)

for current_frame_idx, (interval_start, interval_end) in enumerate(intervals, 1):
    meta.start_frame()
    print(f"Reconstructing frame {current_frame_idx}")

    frame = reconstruct_frame(interval_start, interval_end, current_frame_idx)
    result.append(frame)
    meta.end_frame()

meta.end()
meta.save(output_path)
print(f"Processing took {meta.total_duration}")
