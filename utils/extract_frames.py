"""Utility script to extract certain frames from a 4D nifty image"""

import nibabel as nib

START_IDX = 40
STOP_IDX = 41  # Inclusive end


img = nib.load(
    "/home/recon/Documents/Thesis-Dellekart/PET-Recon-Toolbox-Comparison/results/JSRecon/GPU/result.nii"
)
subset = nib.Nifti1Image(
    img.get_fdata()[:, :, :, START_IDX : STOP_IDX + 1],
    affine=img.affine,
    header=img.header,
)
nib.save(subset, "result.nii.gz")

print()
