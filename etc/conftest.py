""" content of conftest.py
This file is used to add optional features to pytest

Currently it features
    * Optionally running tests marked as 'slow'
"""
import pytest


def pytest_addoption(parser):
    """Add option for running tests marked as 'slow'"""
    parser.addoption("--runslow", action="store_true",
                     help="run slow tests")


def pytest_runtest_setup(item):
    """Setup extra options for pytest"""
    if 'slow' in item.keywords and not item.config.getoption("--runslow"):
        pytest.skip("need --runslow option to run")
