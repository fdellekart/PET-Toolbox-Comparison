# PET Listmode Reconstruction with SIRF Toolbox

The [SIRF](https://github.com/SyneRBI/SIRF) toolbox provides a wrapper around the [STIR](https://github.com/UCL/STIR) reconstruction framework and convenient docker images to avoid installing STIR directly on the machine or building it from source.

An easy to use Python API is provided in combination with many useful examples in the [SIRF-Exercises Repo](https://github.com/SyneRBI/SIRF-Exercises).

The reconstruction implemented herein is based on [this example notebook](https://github.com/SyneRBI/SIRF-Exercises/blob/master/notebooks/PET/reconstruct_measured_data.ipynb) and reconstructs listmode data acquired with the Siemens Biograph mMR system.
It is running inside a container based on the ghcr.io/synerbi/sirf image.

To run the reconstruction pipeline, clone this repository and create directories `input` and `output` inside the `SIRF-STIR` directory.

The following files must be present inside the input directory:
- hardware_umap.nii
- `.dcm` and `.bf` files for listmode data
- `.dcm` and `.bf` files for normalization
- A directory called `MRAC` with MRAC images (`.IMA` files)

When all those files are present you can start the pipeline by running `./run_recon.sh`.
The container will convert the Siemens input files to the STIR data format if files in this format are not yet present.

To change the time interval or frame length edit the variable on top of `run_recon.sh`.
The container also provides a `sleep` entrypoint for debugging purposes
which just runs `sleep infinity` as the container entrypoint.

Results are written to the `output` directory:
- `result.nii.gz` as the resulting image
- `metadata.json` with information about settings and timings
