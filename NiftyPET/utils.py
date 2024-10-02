import numpy as np
from niftypet.nimpa import getnii
from miutil.plot import apply_cmap, imscroll
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter


def div_nzer(x, y):
    return np.divide(x, y, out=np.zeros_like(y), where=y != 0)


def trimVol(x):
    return x[:, 100:-100, 100:-100]


def mapVol(vol, cmap=None, vmin=0, vmax=None):
    msk = ~np.isnan(vol)
    if vmin is None:
        vmin = vol[msk].min()
    if vmax is None:
        vmax = vol[msk].max()
    vol = (np.clip(vol, vmin, vmax) - vmin) / (vmax - vmin)
    return apply_cmap(**{cmap: vol}) if cmap is not None else vol


def register_spm(ref_file, mov_file, opth):
    """
    ref_file  : e.g. recon['fpet']
    mov_file  : e.g. datain['T1nii']
    """
    from spm12.regseg import coreg_spm, resample_spm

    reg = coreg_spm(ref_file, mov_file, outpath=opth, save_arr=False, save_txt=False)
    return getnii(
        resample_spm(
            ref_file,
            mov_file,
            reg["affine"],
            outpath=opth,
            del_ref_uncmpr=True,
            del_flo_uncmpr=True,
            del_out_uncmpr=True,
        )
    )


def register_dipy(ref_file, mov_file, ROI=None):
    """
    ref_file  : e.g. recon['fpet']
    mov_file  : e.g. datain['T1nii']
    """
    from brainweb import register

    return register(
        getnii(mov_file),
        getnii(ref_file),
        ROI=ROI or ((0, None), (100, -100), (100, -100)),
    )


def inspect_img(img: np.array, frame_n: int) -> None:
    """Show raw and smoothed version of the frame from `img`
    specified with `frame_n` as a scrollable image."""
    vmax = np.percentile(img["im"][frame_n], 99.95)
    imscroll(
        {
            "PET": mapVol(trimVol(img["im"][frame_n]), "magma", vmax=vmax),
            "Smoothed": mapVol(
                gaussian_filter(trimVol(img["im"][frame_n]), 4.5 / np.array([4, 4, 4])),
                "magma",
                vmax=vmax,
            ),
        },
        fig=plt.figure(figsize=(9.5, 3.5), tight_layout=True, frameon=False),
    )

    plt.show()
