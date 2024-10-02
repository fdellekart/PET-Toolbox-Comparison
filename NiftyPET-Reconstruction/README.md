# PET Listmode Reconstruction with NiftyPET Toolbox

The [NiftyPET](https://niftypet.readthedocs.io/en/latest/) toolbox is a Python interface for GPU accelerated PET image reconstruction.

The reconstruction implemented herein is based on [this demo](https://niftypet.readthedocs.io/en/latest/tutorials/demo/) and reconstructs listmode data acquired with the Siemens Biograph mMR system.

To run the reconstruction pipeline, clone this repository and create directories `input` and `output` inside the project directory.
It is running inside a docker container.

The following files/directories must be present inside the input directory:
- mumap (Directory with MRAC mumaps)
- hmumap.npz
- listmode.bf
- listmode.dcm
- norm.bf
- norm.dcm

NiftyPET very intelligently detects the required files from the input folder, so the naming should be irrelevant.

When all this files are present you can start the pipeline by running `docker compose up --build --remove-orphans`.

Results are written to the `output` directory.
