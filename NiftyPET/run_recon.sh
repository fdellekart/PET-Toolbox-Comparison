#!/bin/bash

# NiftyPET has a bug that leads to exceptions for empty frames
# Start seven frames later to avoid the first frames without activity
TIME_START=210
TIME_END=3180
TIME_STEP=30

GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)
WORKDIR=/var/work

docker build --build-arg=GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA -t niftypet-recon-$GIT_COMMIT_SHORT_SHA .
docker run --gpus=all -v ${PWD}/input:${WORKDIR}/input -v ${PWD}/output:${WORKDIR}/output niftypet-recon-$GIT_COMMIT_SHORT_SHA recon $TIME_START $TIME_END $TIME_STEP
