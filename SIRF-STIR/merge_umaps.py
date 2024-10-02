"""Utility script to merge nifty files of hardware and subject mumap.

Parameters are: <hardware_umap> <human_umap> <output_path>
"""

import sys

import nibabel as nib
from nilearn.image import resample_img

first_path, second_path, outpath = sys.argv[1:]

img1 = nib.load(first_path)
img2 = nib.load(second_path)

img2 = resample_img(img2, target_affine=img1.affine, target_shape=img1.shape)

result_data = img1.get_fdata() + img2.get_fdata()
result_img = nib.Nifti1Image(result_data, img1.affine, header=img1.header)

nib.save(result_img, outpath)
