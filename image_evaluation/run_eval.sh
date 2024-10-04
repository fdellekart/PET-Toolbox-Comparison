#!/bin/bash

docker build -f Dockerfile-normalize -t image-normalization .
docker build -f Dockerfile-analysis -t image-analysis .

docker run -d -v ./data:/work/data image-normalization
docker wait image-normalization
docker run -d -v ./data:/var/work/data image-analysis
docker wait image-analysis
