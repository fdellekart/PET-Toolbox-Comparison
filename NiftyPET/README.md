# PET Listmode Reconstruction with NiftyPET Toolbox

The [NiftyPET](https://niftypet.readthedocs.io/en/latest/) toolbox is a Python interface for GPU accelerated PET image reconstruction.

The reconstruction implemented herein is based on [this demo](https://niftypet.readthedocs.io/en/latest/tutorials/demo/) and reconstructs listmode data acquired with the Siemens Biograph mMR system.

To run the reconstruction pipeline, clone this repository and create directories `input` and `output` inside the NiftyPET directory.
The reconstruction is running inside a docker container.

The following files/directories must be present inside the input directory:
- mumap (Directory with MRAC mumaps)
- hmumap.npz
- listmode `.dcm` and `.bf` files
- norm `.dcm` and `.bf` files


When all this files are present you can start the pipeline by running `./run_recon.sh`.
To adapt the timeframe settings to reconstruct edit the variables on top of `run_recon.sh`.

Results are written to the `output` directory and consist of a `result.nii.gz` file and
as `metadata.json` with timing information and reconstruction settings.
