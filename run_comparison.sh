#!/bin/bash

# This script runs the reconstruction and evaluation for all
# specified targets and saves images and metadata to results

TARGET_DIRS=(SIRF-STIR NiftyPET)
GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)

printf -v date '%(%Y-%m-%d-%H-%M)T' -1
export OUTPUT_VERSION_DIR=${date}-${GIT_COMMIT_SHORT_SHA}
DESTINATION_PARENT_DIR=${PWD}/results/${OUTPUT_VERSION_DIR}
mkdir "${DESTINATION_PARENT_DIR}"

for target in ${TARGET_DIRS[@]}; do
    DESTINATION_DIR=${DESTINATION_PARENT_DIR}/${target}
    mkdir "${DESTINATION_DIR}"

    cd $target
    ./run_recon.sh
    cp ./output/result.nii.gz ${DESTINATION_DIR}/result.nii.gz
    cp ./output/metadata.json ${DESTINATION_DIR}/metadata.json

    cd ../image_evaluation
    cp ${DESTINATION_DIR}/result.nii.gz ./data/sub-00/pet/result.nii.gz
    ./run_eval.sh
    cp ./data/pet_mni4d.nii.gz ${DESTINATION_DIR}/pet_mni4d.nii.gz
    cp ./data/result.json ${DESTINATION_DIR}/evaluation.json

    cd ..
done
