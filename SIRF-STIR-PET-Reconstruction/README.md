# PET Listmode Reconstruction with SIRF Toolbox

The [SIRF](https://github.com/SyneRBI/SIRF) toolbox provides a wrapper around the [STIR](https://github.com/UCL/STIR) reconstruction framework and convenient docker images to avoid installing STIR directly on the machine or building it from source.

An easy to use Python API is provided in combination with many useful examples in the [SIRF-Exercises Repo](https://github.com/SyneRBI/SIRF-Exercises).

The reconstruction implemented herein is based on [this example notebook](https://github.com/SyneRBI/SIRF-Exercises/blob/master/notebooks/PET/reconstruct_measured_data.ipynb) and reconstructs listmode data acquired with the Siemens Biograph mMR system.
It is running inside a container based on the ghcr.io/synerbi/sirf image.

To run the reconstruction pipeline, clone this repository and create directories `input` and `output` inside the project directory.

The following files must be present inside the input directory:
- hardware_umap.nii
- `.dcm` and `.bf` files for listmode data
- `.dcm` and `.bf` files for normalization
- A directory called `pseudoCT` with MRAC images

When all this files are present you can start the pipeline by running `./run_recon.sh`.
The container will convert the Siemens input files to the STIR data format if files in this format are not yet present.

To change the time interval or frame length edit the parameters in `run_recon.sh`.
Parameters are `recon <time_start> <time_end> <frame_length>`.
The container also provides a `sleep` entrypoint for debugging purposes.

Results are written to the `output` directory.
