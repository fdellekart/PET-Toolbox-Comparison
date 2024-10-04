#!/bin/bash

docker build -f Dockerfile-normalize -t image-normalization .
docker build -f Dockerfile-analysis -t image-analysis .

echo "Normalizing images to MNI space."
docker run -d -v ./data:/work/data image-normalization
docker wait image-normalization

echo "Running image quality evaluation"
docker run -d -v ./data:/var/work/data image-analysis
docker wait image-analysis
