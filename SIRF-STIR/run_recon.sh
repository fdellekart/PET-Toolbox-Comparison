#!/bin/bash

TIME_START=0
TIME_END=3180
TIME_STEP=30

GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)
WORKDIR=/home/jovyan/work/recon

docker container rm sirf-stir-recon
docker container rm fslmerge
if [ "$1" = "--build" ]; then
    docker build --build-arg=GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA -t sirf-recon .
    docker build -f Dockerfile-fslmerge -t fslmerge .
fi

echo "Running reconstruction with SIRF."
echo "To see container logs run 'docker logs -t -f --since=5m sirf-stir-recon'."

container_id=$(docker run -d --name=sirf-stir-recon -v ${PWD}/input:${WORKDIR}/input -v ${PWD}/output:${WORKDIR}/output sirf-recon recon $TIME_START $TIME_END $TIME_STEP)
status_code=$(docker wait sirf-stir-recon)

if [ $status_code -ne 0 ]; then
    echo "Error in SIRF-STIR reconstruction"
    echo "Run 'docker logs ${container_id}' to view container logs"
    exit 1
fi

container_id=$(docker run -d --name=fslmerge -v ${PWD}/output:/work/output fslmerge)
status_code=$(docker wait fslmerge)

if [ $status_code -ne 0 ]; then
    echo "Error in when merging frames using FSL"
    echo "Run 'docker logs ${container_id}' to view container logs"
    exit $status_code
fi
