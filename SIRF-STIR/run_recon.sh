#!/bin/bash

TIME_START=0
TIME_END=3180
TIME_STEP=30

GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)
WORKDIR=/home/jovyan/work/recon

docker build --build-arg=GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA -t sirf-recon-$GIT_COMMIT_SHORT_SHA .
docker run -v ${PWD}/input:${WORKDIR}/input -v ${PWD}/output:${WORKDIR}/output sirf-recon-$GIT_COMMIT_SHORT_SHA recon $TIME_START $TIME_END $TIME_STEP
