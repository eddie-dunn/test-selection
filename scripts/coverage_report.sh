#!/bin/bash
# Run unit, function and integration tests and generate a coverage report

# This variable contains the modules to run coverage report on
COV="diff eval seek sim util"
#COV="diff eval"

pyclean .
py.test-3.4 --cov $COV --cov-report html \
    "$@" diff seek
