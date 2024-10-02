#!/bin/bash
set -e

# Verify if files ending '.l.hdr' and '.n.hdr'
# already exist inside the input directory.
# If yes then set the 'listmodeConvertedExists' or
# 'normConvertedExists' variables
check_stir_files_exist () {
    if [ -f ./input/*.l.hdr ]; then
        listmodeConvertedExists=1
    fi
    if [ -f ./input/*.n.hdr ]; then
        normConvertedExists=1
    fi
}

# Check if unconverted listmode and norm files
# are present in input directory and set the
# 'listmodeFile' and 'normFile' variables if found.
verifyInputs () {
    for dcmFile in ./input/*.dcm; do
        secondline=$(cat $dcmFile | head -2 | tail -1)
        if [[ $secondline == *"PET_NORM"* ]]; then
            normFile=$dcmFile
        else if [[ $secondline == *"PET_LISTMODE"* ]]; then
            listmodeFile=$dcmFile
            fi
        fi
    done
}

# If listmode or norm files already exist in converted form do nothing.
# If Siemens data is available convert it to STIR format.
# If both are missing exit with error.
extractOnDemand() {
    if [ ! $listmodeConvertedExists ] && [ ! $listmodeFile ]; then
        echo "ERROR: Neither STIR interfile format listmode file present in input nor raw Siemens data"
        exit 1
    else if [ ! $listmodeConvertedExists ]; then
        nm_extract -i $listmodeFile
        fi
    fi
    if [ ! $normConvertedExists ] && [ ! $normFile ]; then
        echo "ERROR: Neither STIR interfile format norm file present in input nor raw Siemens data"
        exit 1
    else if [ ! $normConvertedExists ]; then
        nm_extract -i $normFile
        fi
    fi
}

if [ "$1" = 'recon' ]; then
    check_stir_files_exist
    verifyInputs
    extractOnDemand
    nm_mrac2mu -i ./input/pseudoCT -o ./output/human_mumap.nii || true  # Fails in the end but file is still output
    python merge_umaps.py ./input/hardware_umap.nii ./output/human_mumap.nii ./output/combined_mumap.nii
    python recon.py $2 $3 $4
else if [ "$1" = 'sleep' ]; then
        sleep infinity
else
        exec "$@"
    fi
fi
