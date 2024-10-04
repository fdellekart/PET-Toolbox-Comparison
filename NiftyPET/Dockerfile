FROM nvidia/cuda:12.6.0-devel-ubuntu22.04

ARG GIT_COMMIT_SHORT_SHA
ENV GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA

RUN apt-get update && \
    apt-get install -y python3.10-venv python3.10-dev python-is-python3 build-essential cmake git && \
    rm -rf /var/lib/apt/lists/*
RUN ["mkdir", "/var/work"]
WORKDIR /var/work

COPY requirements.txt requirements.txt

RUN ["python", "-m", "venv", "reco-venv"]
RUN ["reco-venv/bin/pip", "install", "--upgrade", "pip"]
RUN ["reco-venv/bin/pip", "install", "-r", "requirements.txt"]
RUN ["reco-venv/bin/pip", "install", "git+https://github.com/fdellekart/NIPET.git@measure-timing"]

COPY utils.py uitls.py
COPY recon.py recon.py

COPY docker-entrypoint.sh docker-entrypoint.sh
RUN ["chmod", "+x", "/var/work/docker-entrypoint.sh"]

ENTRYPOINT [ "/var/work/docker-entrypoint.sh" ]
