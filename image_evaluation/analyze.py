import json

import numpy as np
import nibabel as nib
from nilearn.datasets import fetch_atlas_aal

NORM_IMAGE_FILE = "data/pet_mni4d.nii.gz"

atlas_meta = fetch_atlas_aal()
atlas = nib.load(atlas_meta["maps"]).get_fdata().astype(np.int16)
image_sequence = nib.load(NORM_IMAGE_FILE).get_fdata()

labels = np.array(atlas_meta["labels"])
indices = np.array(atlas_meta["indices"]).astype(np.int16)

is_cerebelum = np.char.startswith(labels, "Cerebelum")
cerebelum_ids = indices[is_cerebelum]
other_ids = indices[~is_cerebelum]


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


def get_cnrs(image: np.array) -> dict:
    results = dict()
    results["cnr_per_region"] = dict()

    image[image < 0] = 0
    is_cerebelum = np.isin(atlas, cerebelum_ids)
    cerebelum_mean = image[is_cerebelum].mean()
    cerebelum_std = image[is_cerebelum].std()

    for index in map(int, other_ids):
        mask = atlas == index
        results["cnr_per_region"][index] = (
            image[mask].mean() - cerebelum_mean
        ) / cerebelum_std

    return results


results = []
for i in range(image_sequence.shape[-1]):
    image = image_sequence[:, :, :, i]
    results.append(dict(**get_snrs(image), **get_cnrs(image)))

with open("./data/result.json", "w") as f:
    json.dump(results, f)
