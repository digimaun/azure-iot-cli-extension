#!/usr/bin/env bash
set -e

proc_number=`python -c 'import multiprocessing; print(multiprocessing.cpu_count())'`

# Run pylint/flake8 on IoT extension
pylint azext_iot/ --ignore=events3 --rcfile=./.pylintrc -j $proc_number
flake8 azext_iot/ --statistics --exclude=events3 --config=setup.cfg
