from __future__ import print_function, division
from os import path, getenv, listdir, mkdir
import logging
import sys
import shutil
from pathlib import Path
from datetime import datetime

from niftypet import nipet
from niftypet import timer as meta
import numpy as np


output_path = Path(
    f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M')}_{getenv('GIT_COMMIT_SHORT_SHA')}"
)
mkdir(output_path)

TIME_START, TIME_END, TIME_STEP = map(int, sys.argv[1:])
meta.add_metadatum("time_start", TIME_START)
meta.add_metadatum("time_end", TIME_END)
meta.add_metadatum("time_step", TIME_STEP)
meta.add_metadatum("num_subsets", 14)

meta.start()

logging.basicConfig(level=logging.INFO)
print(nipet.gpuinfo())

mMRpars = nipet.get_mmrparams("input")
mMRpars["Cnt"]["DEVID"] = 0
mMRpars["Cnt"]["SPN"] = meta.add_metadatum("span", 11)


# conversion for Gaussian sigma/[voxel] to FWHM/[mm]
SIGMA2FWHMmm = (
    (8 * np.log(2)) ** 0.5 * np.array([mMRpars["Cnt"]["SO_VX" + i] for i in "ZYX"]) * 10
)

folderin = "./input/"
folderout = "."  # realtive to `{folderin}/niftyout`
itr = meta.add_metadatum(
    "num_subiterations", 7
)  # number of iterations (will be multiplied by 14 for MLEM)
fwhm = meta.add_metadatum("psf_fwhm", 4)  # mm (for resolution modelling)

folderin = path.expanduser(folderin)
datain = nipet.classify_input(folderin, mMRpars, recurse=-1)

outpath = path.join(datain["corepath"], "niftyout")

# the same as above without any faff though (no alignment)
mu_o = nipet.obj_mumap(datain, mMRpars, outpath=outpath, store=True)

# hardware mu-map (bed, head/neck coils)
mu_h = nipet.hdw_mumap(datain, [1, 2, 4], mMRpars, outpath=outpath, use_stored=True)

# built-in default: 14 subsets
fcomment = f"_fwhm-{fwhm}_recon"
outpath = path.join(outpath, folderout)
timings = [
    [TIME_START + idx * TIME_STEP, TIME_START + (idx + 1) * TIME_STEP]
    for idx in range((TIME_END - TIME_START) // TIME_STEP)
]

recon = nipet.mmrchain(
    datain,
    mMRpars,
    frames=["timings", *timings],
    itr=itr,
    mu_h=mu_h,
    mu_o=mu_o,
    psf=fwhm,
    recmod=3,
    outpath=outpath,
    fcomment=fcomment,
    store_img=True,
)

meta.end()
meta.save(output_path)
nifty_file = next(
    filter(lambda filename: filename.endswith(".nii.gz"), listdir("./input/niftyout/"))
)
shutil.copy(
    Path(folderin) / "niftyout" / "PET" / "multiple-frames" / nifty_file,
    output_path / "result.nii.gz",
)
