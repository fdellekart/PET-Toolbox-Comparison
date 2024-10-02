# Image Evaluation for Reconstructed fPET data

This repository serves to compare fPET images reconstructed with different
reconstruction toolboxes with regards to image quality.

To provide comparable results, the following preprocessing steps are executed:

- Motion correction of dynamic PET data
- Coregistration with a T1 MRI image
- Normalization of T1 to MNI space
- Normalization of PET data with the obtained transformation

All those steps are executed using the FSL toolbox inside `./normalize.sh`.

**WARNING**: the normalization of all PET frames is executed in parallel
with 32 parallel processes, which requires up to 300 GB of RAM,
if you don't have that then decrease the `N_PROCS` variable inside `./normalize.sh`.

In `analysis.py` negative values are first set to 0.
Subsequently, the signal to noise ration (SNR) is calculated per region of the AAL brain atlas, where the SNR is defined as the ratio of mean to standard deviation.

The results ar written to a json file.

`normalize.sh` relies on FSL being installed on the system.
To avoid the installation, we run everything inside a docker container with FSL installed.

To run the pipeline first run:

```
docker build -t image_eval .
```

And then execute the container and mount a data directory into it as a volume:

```
docker run -v ./data/:/work/data image_eval
```

TODO: Add information about what data needs to be present in data directory
