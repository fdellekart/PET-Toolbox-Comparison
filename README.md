# PET Toolbox Comparison

This repository is the result of a master's thesis comparing
openly available toolboxes for positron emission tomography (PET) image reconstruction
in the context of functional PET (fPET) for neuroscience.
The directories `NiftyPET` and `SIRF-STIR` contain the code and setup
for reconstructions using the two toolboxes. For further details consult the
respective README files in the directories.

The `image_evaluation` directory contains a workflow to first normalize results
to MNI space and then compute image quality metrics per brain region.
It is executed by `image_evaluation/run_eval.sh` script and operates on
data inside the `image_evaluation/data` directory. For further information
please refer to the README file in the directory.

The `plotting` directory contains various scripts and utilities for plotting
the results.

The full thesis is available [here](https://doi.org/10.34726/hss.2025.123400).
