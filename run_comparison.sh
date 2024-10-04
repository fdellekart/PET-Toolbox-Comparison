#!/bin/bash

# This script runs the reconstruction and evaluation for all
# specified targets and saves images and metadata to results

TARGET_DIRS=(SIRF-STIR NiftyPET)
GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)

printf -v date '%(%Y-%m-%d-%H-%M)T' -1
export OUTPUT_VERSION_DIR=${date}-${GIT_COMMIT_SHORT_SHA}
DESTINATION_PARENT_DIR=${PWD}/results/${OUTPUT_VERSION_DIR}
mkdir "${DESTINATION_PARENT_DIR}"

# Function to capture stats and append them to CSV
capture_stats() {
    gpu_stats=$(nvidia-smi -i $GPU_DEVICE_ID --query-gpu memory.used,utilization.gpu --format=csv,noheader)
    docker stats --no-stream --format \
    "{{.CPUPerc}},{{.MemPerc}},{{.MemUsage}},{{.BlockIO}}" $CONTAINER_NAME | \
    while IFS= read -r line; do
        # Get current timestamp
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        # Append to CSV with timestamp
        echo "$timestamp,$line,$gpu_stats" >> $STAT_LOG_PATH
    done
}

for target in ${TARGET_DIRS[@]}; do
    DESTINATION_DIR=${DESTINATION_PARENT_DIR}/${target}
    CONTAINER_NAME="$(echo "$target" | tr '[:upper:]' '[:lower:]')-recon"
    STAT_LOG_PATH=${DESTINATION_DIR}/resources.csv
    echo "Stat log path: ${STAT_LOG_PATH}"

    mkdir "${DESTINATION_DIR}"
    echo "Timestamp,CPU_Usage(%),Memory_Usage(%),Memory_Usage/Limit,Block_I/O,GPU_Memory,GPU_Utilization" > $STAT_LOG_PATH

    cd $target

    ./run_recon.sh /dev/null 2>&1 &
    task_pid=$!
    while kill -0 "$task_pid" 2>/dev/null; do
        capture_stats
        sleep 1
    done
    wait "$task_pid"

    cp ./output/result.nii.gz ${DESTINATION_DIR}/result.nii.gz
    cp ./output/metadata.json ${DESTINATION_DIR}/metadata.json

    cd ../image_evaluation
    cp ${DESTINATION_DIR}/result.nii.gz ./data/sub-00/pet/result.nii.gz
    ./run_eval.sh
    cp ./data/pet_mni4d.nii.gz ${DESTINATION_DIR}/pet_mni4d.nii.gz
    cp ./data/result.json ${DESTINATION_DIR}/evaluation.json

    cd ..
done
