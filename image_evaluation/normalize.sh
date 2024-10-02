#!/bin/bash

normalize_frame(){
    idx=$1;
    echo "Normalizing frame with idx $idx..."
    
    # Extract the frame_idx-th frame
    fslroi pet_mc pet_mc_frame_${idx} $idx 1
    flirt -in pet_mc_frame_${idx} -ref $T1_IMAGE -applyxfm -init pet2t1.mat -out pet_coreg_frame_${idx}

    # Apply the transformation to the current frame
    applywarp --in=pet_coreg_frame_${idx} --ref=$MNI_TEMPLATE --warp=t1_2_mni_warp --out=pet_mni_frame_${idx} --interp=spline
}

N_PROCS=32

# Set up paths
PET_IMAGE="data/sub-00/pet/result_span11.nii"  # Path to the 4D dynamic PET image
T1_IMAGE="data/sub-00/anat/sub-00_T1w.nii"        # Path to the T1-weighted anatomical MRI image
MNI_TEMPLATE="/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm.nii.gz"  # Path to MNI template (2mm resolution)
MNI_BRAIN_MASK="/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain_mask.nii.gz"

n_frames=$(fslnvols $PET_IMAGE)  # Get the number of frames in the 4D image

echo "Performing motion correction on dynamic PET data..."
mcflirt -in $PET_IMAGE -out pet_mc -plots

echo "Coregistering mean PET image to T1-weighted MRI..."
fslmaths pet_mc -Tmean pet_mean
flirt -in pet_mean -ref $T1_IMAGE -out pet_coreg -omat pet2t1.mat

echo "Normalizing T1-weighted MRI to MNI space..."
flirt -in $T1_IMAGE -ref $MNI_TEMPLATE -out t1_mni_linear -omat t12mni.mat
fnirt --ref=$MNI_TEMPLATE --refmask=$MNI_BRAIN_MASK --in=$T1_IMAGE --aff=t12mni.mat --cout=t1_2_mni_warp --config="/usr/share/fsl/5.0/etc/flirtsch/T1_2_MNI152_2mm.cnf"

echo "Normalizing each PET frame to MNI space with ${N_PROCS} in parallel..."

# WARNING: this is fairly hungry for RAM
# Turn down N-procs in case it's a problem
( 
for (( frame_idx=0; frame_idx<n_frames; frame_idx++ )); do
    ((i=i%N_PROCS)); ((i++==0)) && wait
    normalize_frame "$frame_idx" &
done
wait
)

echo "Merging normalized frames into a 4D image..."
fslmerge -t pet_mni_4d $(ls pet_mni_frame_*.nii.gz | sort -V)

# If DEBUG is set then copy all intermediate files to results
if [ $DEBUG ]; then
    cp *.nii.gz ./data/
    cp *.mat ./data/
else
    cp pet_mni_4d.nii.gz ./data/pet_mni4d.nii.gz
fi
