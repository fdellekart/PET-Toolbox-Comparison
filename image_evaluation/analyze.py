import json

import numpy as np
import nibabel as nib
from nilearn.datasets import fetch_atlas_aal

NORM_IMAGE_FILE = "data/pet_mni4d.nii.gz"


def get_snrs(image: np.array) -> dict:
    results = dict()
    snr_per_region = dict()
    results["snr_per_region"] = snr_per_region

    image[image < 0] = 0

    for index in map(int, atlas_meta["indices"]):
        subset = image[atlas == index]
        snr_per_region[index] = subset.mean() / subset.std()

    subset = image[atlas != 0]
    results["total_snr"] = subset.mean() / subset.std()

    return results


atlas_meta = fetch_atlas_aal()
atlas = nib.load(atlas_meta["maps"]).get_fdata().astype(np.int16)
image_sequence = nib.load(NORM_IMAGE_FILE).get_fdata()

results = []
for i in range(image_sequence.shape[-1]):
    image = image_sequence[:, :, :, i]
    results.append(get_snrs(image))

with open("./data/result.json", "w") as f:
    json.dump(results, f)
