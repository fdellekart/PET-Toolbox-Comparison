import json

import numpy as np
import nibabel as nib
from nilearn.datasets import fetch_atlas_aal

NORM_IMAGE_FILE = "data/pet_mni4d_jsrecon.nii.gz"

results = dict()
results["norm_file"] = NORM_IMAGE_FILE
atlas_meta = fetch_atlas_aal()

atlas = nib.load(atlas_meta["maps"]).get_fdata().astype(np.int16)
image = nib.load(NORM_IMAGE_FILE).get_fdata()
image = image[:, :, :, 86]
image[image < 0] = 0

snr_per_region = dict()
results["snr_per_region"] = snr_per_region

for index in map(int, atlas_meta["indices"]):
    subset = image[atlas == index]
    snr_per_region[index] = subset.mean() / subset.std()

subset = image[atlas != 0]
results["total_snr"] = subset.mean() / subset.std()

with open("results.json", "w") as f:
    json.dump(results, f)
