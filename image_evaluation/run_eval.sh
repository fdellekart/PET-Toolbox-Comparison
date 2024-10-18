#!/bin/bash



docker container rm image-normalization
docker container rm image-analysis

if [ "$1" = "--build" ]; then
    docker build -f Dockerfile-normalize -t image-normalization .
    docker build -f Dockerfile-analysis -t image-analysis .
fi

echo "Normalizing images to MNI space."
container_id=$(docker run -d --name=image-normalization -v ./data:/work/data image-normalization)
status_code=$(docker wait image-normalization)

if [ $status_code -ne 0 ]; then
    echo "Error in image normalization"
    echo "Run 'docker logs ${container_id}' to view container logs"
    exit $status_code
fi

echo "Running image quality evaluation"
container_id=$(docker run -d --name=image-analysis -v ./data:/var/work/data image-analysis)
status_code=$(docker wait image-analysis)

if [ $status_code -ne 0 ]; then
    echo "Error in image quality evaluation"
    echo "Run 'docker logs ${container_id}' to view container logs"
    exit $status_code
fi
