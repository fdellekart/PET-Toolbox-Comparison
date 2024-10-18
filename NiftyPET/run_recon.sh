#!/bin/bash

# NiftyPET has a bug that leads to exceptions for empty frames
# Start seven frames later to avoid the first frames without activity
TIME_START=1200
TIME_END=1260
TIME_STEP=30

GIT_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)
WORKDIR=/var/work

docker container rm niftypet-recon
docker build --build-arg=CACHEBUST=$(date +%s) --build-arg=GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA -t niftypet-recon .

echo "Running reconstruction with NiftyPET."
echo "To see container logs run 'docker logs -t -f --since=5m niftypet-recon'."

container_id=$(docker run -d --name=niftypet-recon --gpus=all -v ${PWD}/input:${WORKDIR}/input -v ${PWD}/output:${WORKDIR}/output niftypet-recon recon ${TIME_START} ${TIME_END} ${TIME_STEP})
status_code=$(docker wait niftypet-recon)

if [ $status_code -ne 0 ]; then
    echo "Error in reconstruction with NiftyPET"
    echo "Run 'docker logs ${container_id}' to view container logs"
    exit $status_code
fi
