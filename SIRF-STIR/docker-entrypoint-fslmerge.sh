#!/bin/bash

fslmerge -t ./output/result $(ls ./output/frame_*.nii | sort -V)
rm $(ls ./output/frame_*.nii)
