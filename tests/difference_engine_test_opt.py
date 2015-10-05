"""Tests for difference engine"""
import diff.difference_engine as difference_engine

from util.util import Build
from util.util import BuildSet

# import pytest  # import this for e.g. pytest.mark.xfail
import unittest
from collections import OrderedDict

# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint:disable=bad-whitespace,invalid-name
# pylint:disable=no-self-use

# Tests for test flips
# ====================
#    ______ _ _
#   |  ____| (_)
#   | |__  | |_ _ __  ___
#   |  __| | | | '_ \/ __|
#   | |    | | | |_) \__ \
#   |_|    |_|_| .__/|___/
#              |_|
def test_flips_are_correct1():
    build1 = {'tests': {'pass': ['A'], 'fail': ['B']}}
    build2 = {'tests': {'pass': [], 'fail': ['A', 'C']}}
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['A'])

def test_flips_are_correct2():
    build1 = {'tests': {'pass': ['A'], 'fail': ['B']}}
    build2 = {'tests': {'pass': [], 'fail': ['A', 'B']}}
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['A'])

def test_flips_are_correct3():
    # pylint: disable=line-too-long
    build1 = {'tests': {'pass': ['A'], 'fail': ['B', 'C']}}
    build2 = {'tests': {'pass': ['C'], 'fail': ['A', 'B']}}
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['A', 'C'])

def test_flips_are_correct4_opt():
    build1 = {'tests': {'pass': ['1', '3'], 'fail': ['2', '4']}}
    build2 = {'tests': {'pass': ['1'], 'fail': ['2', '4', '3', '5']}}
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['3'])

def test_flips_are_correct5_opt():
    build2 = {'tests': {'pass': ['1', '3'], 'fail': ['2', '4']}}
    build1 = {'tests': {'pass': ['1'], 'fail': ['2', '4', '3', '5']}}
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['3'])