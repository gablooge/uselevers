#!/usr/bin/env bash

set -e
set +x # Turn off debug mode

mypy .
ruff .
ruff format . --check
flake8 .
black --check --diff .
bandit -c .bandit.yml -r *

if [[ -n "$1" && "$1" == "--include-safety" ]]; then
    echo "Running safety check..."
    if [ ! -e "insecure_full.json" ]; then
        wget https://github.com/pyupio/safety-db/raw/master/data/insecure_full.json
    fi
    if [ ! -e "insecure.json" ]; then
        wget https://github.com/pyupio/safety-db/raw/master/data/insecure.json
    fi
    safety check --ignore=64459 --ignore=64396 --full-report
fi
