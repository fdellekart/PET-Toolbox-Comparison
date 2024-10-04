#!/bin/bash

docker container rm image-normalization
docker container rm image-analysis

docker build -f Dockerfile-normalize -t image-normalization .
docker build -f Dockerfile-analysis -t image-analysis .

echo "Normalizing images to MNI space."
docker run -d --name=image-normalization -v ./data:/work/data image-normalization
docker wait image-normalization

echo "Running image quality evaluation"
docker run -d --name=image-analysis -v ./data:/var/work/data image-analysis
docker wait image-analysis
