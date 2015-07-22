#!/usr/bin/env bash
#==================
# This scripts counts the LOC of all python files found from the root dir

find . -not \( -path "./venv/*" -prune \) -name '*.py' | xargs wc -l
