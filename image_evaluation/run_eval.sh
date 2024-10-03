#!/bin/bash

docker build -t image-eval .
docker run -v ./data:/work/data image-eval

python analyze.py
