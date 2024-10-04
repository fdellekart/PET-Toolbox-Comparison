#!/bin/bash

TIME_START=1200
TIME_END=1260
TIME_STEP=30

GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)
WORKDIR=/home/jovyan/work/recon

docker container rm sirf-stir-recon
docker build --build-arg=GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA -t sirf-recon .

echo "Running reconstruction with SIRF."
echo "To see container logs run 'docker logs -t -f --since=5m sirf-stir-recon'."

docker run -d --name=sirf-stir-recon -v ${PWD}/input:${WORKDIR}/input -v ${PWD}/output:${WORKDIR}/output sirf-recon recon $TIME_START $TIME_END $TIME_STEP
docker wait sirf-stir-recon
