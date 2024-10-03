#!/bin/bash

docker build -f Dockerfile-normalize -t image-normalization .
docker build -f Dockerfile-analysis -t image-analysis .

docker run -v ./data:/work/data image-normalization
docker run -v ./data:/var/work/data image-analysis
