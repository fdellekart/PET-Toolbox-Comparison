#!/bin/sh
set -e

if [ "$1" = 'recon' ]; then
    reco-venv/bin/python recon.py $2 $3 $4
else if [ "$1" = 'sleep' ]; then
        sleep infinity
else
        exec "$@"
    fi
fi
