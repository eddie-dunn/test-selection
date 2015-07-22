# -*- coding: utf-8 -*-
"""Tests for sim2.py"""
import diff.simulatron.sim2 as sim2
from util.util import json_loads

import unittest
from collections import Counter

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-many-public-methods
# pylint: disable=no-self-use

# from unittest.mock import patch
# from unittest.mock import MagicMock
# mock_rand = MagicMock(side_effect=[num for num in range(10)])


# Test generate buildsets
# #######################

def test_generate_buildset_to_json():
    pkg_mappings = {'hej': 'hej.test'}
    buildset = sim2.generate_buildset(size=2, mappings=pkg_mappings)
    json_buildset = buildset.json(indent=4)
    dict_buildset = dict(json_loads(json_buildset))
    assert '0' in dict_buildset

def test_generate_buildset_0():
    paknames = ['pak1', 'pak2', 'pak3']
    mappings = {pak: "{}.test".format(pak) for pak in paknames}
    size = 5
    buildset = sim2.generate_buildset(size, mappings, seed=3)
    correct_set_first = {"0": {"tests": [("pak1.test", "fail"),
                                         ("pak2.test", "pass"),
                                         ("pak3.test", "pass"),
                                        ],
                               "modules": [("pak1", "Xrev1"),
                                           ("pak2", "rev0"),
                                           ("pak3", "rev0")]
                               }
                        }
    assert buildset.dict['0'] == correct_set_first["0"]
    # NOTE: This only checks that the first build in buildset is correct. A
    # tests checking the correctness of the full generated dict might be
    # required later on


# Tests for name generators (modules and tests)
# #############################################

def test_generate_package_names():
    prefix = 'pak'
    names = sim2.generate_pkg_names(10, prefix=prefix)
    for name, number in zip(names, range(len(names))):
        # Make sure the pkg numbers are in order
        assert name.replace(prefix, '') == str(number)


def test_pkgmappings():
    pkgnames = ['pak1', 'pak2', 'pak4', 'pak55']
    mappings = sim2.pkgmappings(pkgnames, test_suffix='.tst')
    assert mappings == {'pak1': 'pak1.tst',
                        'pak2': 'pak2.tst',
                        'pak4': 'pak4.tst',
                        'pak55': 'pak55.tst'}


# import pytest
# @pytest.mark.xfail
# def test_xfail():
#     assert False


class IntegrationTests(unittest.TestCase):
    """More complicated tests involving more parts of the sim2 functions"""
    def test_create_superset(self):
        # NOTE This test fails for unknown reasons, but probably due to
        # dict/set hashing being in a different order in Python3. This might
        # lead to problems, so it can be worthwhile to get back to this later
        nbr_paks = 10
        superset = sim2.create_superset(packages=nbr_paks, pkg_noise=100,
                                        test_noise=100, seed=1, builds=2)
        testnames = ['pak{}.test'.format(num) for num in range(nbr_paks)]
        tests = [(name, 'pass') for name in testnames]
        # Check that modules are correct
        assert nbr_paks == len(superset['prod0']['0']['modules'])
        assert set(superset['prod0']['0']['modules']) == set([('pak0', 'rev0'),
                                                              ('pak1', 'Xrev1'),
                                                              ('pak2', 'rev1'),
                                                              ('pak3', 'rev1'),
                                                              ('pak4', 'rev0'),
                                                              ('pak5', 'rev0'),
                                                              ('pak6', 'rev0'),
                                                              ('pak7', 'rev0'),
                                                              ('pak8', 'rev0'),
                                                              ('pak9', 'rev0')]
                                                         )

        assert superset['prod0']['1']['modules'] == [('pak0', 'rev0'),
                                                     ('pak1', 'Xrev2'),
                                                     ('pak2', 'rev2'),
                                                     ('pak3', 'rev2'),
                                                     ('pak4', 'rev0'),
                                                     ('pak5', 'rev0'),
                                                     ('pak6', 'rev0'),
                                                     ('pak7', 'rev0'),
                                                     ('pak8', 'rev0'),
                                                     ('pak9', 'rev0')]
        # Check that tests are correct
        assert len(tests) == len(superset['prod0']['0']['tests'])
        assert superset['prod0']['0']['tests'] == [('pak0.test', 'pass'),
                                                   ('pak1.test', 'fail'),
                                                   ('pak2.test', 'fail'),
                                                   ('pak3.test', 'fail'),
                                                   ('pak4.test', 'pass'),
                                                   ('pak5.test', 'pass'),
                                                   ('pak6.test', 'pass'),
                                                   ('pak7.test', 'pass'),
                                                   ('pak8.test', 'pass'),
                                                   ('pak9.test', 'pass')]

        # the next test set will flip the same tests as in the first set, so
        # that means that they will change back to pass, meaning that all tests
        # will pass
        assert superset['prod0']['1']['tests'] == [('pak0.test', 'pass'),
                                                   ('pak1.test', 'pass'),
                                                   ('pak2.test', 'pass'),
                                                   ('pak3.test', 'pass'),
                                                   ('pak4.test', 'pass'),
                                                   ('pak5.test', 'pass'),
                                                   ('pak6.test', 'pass'),
                                                   ('pak7.test', 'pass'),
                                                   ('pak8.test', 'pass'),
                                                   ('pak9.test', 'pass')]

    def test_several_supersets_differ(self):
        superset1 = sim2.create_superset()
        superset2 = sim2.create_superset()
        assert superset1 != superset2

    #@pytest.mark.xfail
    def test_not_same_tests_changed_in_consecutive_runs(self):
        superset = sim2.create_superset(pkg_noise=2, test_noise=5)
        bid0_tests = superset['prod0']['0']['tests']
        bid1_tests = superset['prod0']['1']['tests']
        assert bid0_tests != bid1_tests

    def test_not_same_paks_changed_in_consecutive_runs(self):
        superset = sim2.create_superset(pkg_noise=2, test_noise=5)
        bid0_paks = superset['prod0']['0']['modules']
        bid1_paks = superset['prod0']['1']['modules']
        assert bid0_paks != bid1_paks

    def test_no_dupes_of_tests_in_superset(self):
        for _ in range(100):
            superset = sim2.create_superset(pkg_noise=2, test_noise=4)
            bid0_tests = superset['prod0']['0']['tests']
            names0 = [item[0] for item in bid0_tests]
            count_names = Counter(names0)
            for val in count_names.values():
                assert val < 2, "dupes found in {}".format(names0)

    def test_no_dupes_of_tests_in_superset1(self):
        for _ in range(100):
            superset = sim2.create_superset(pkg_noise=2, test_noise=4)
            bid0_tests = superset['prod0']['0']['tests']
            bid1_tests = superset['prod0']['1']['tests']

            counter0 = Counter(bid0_tests)
            for val in counter0.values():
                assert val < 2, "dupes found: {}".format(bid0_tests)

            counter1 = Counter(bid1_tests)
            for val in counter1.values():
                assert val < 2, "dupes found: {}".format(bid1_tests)


# test newrev
# ===========

def test_newrev_1():
    rev = 'rev0'
    newrev = sim2.newrev(rev, mark=False)
    assert newrev == 'rev1'

def test_newrev_2():
    rev = 'rev0'
    newrev = sim2.newrev(rev, mark=True)
    assert newrev == 'Xrev1'

def test_newrev_3():
    rev = 'Xrev1'
    newrev = sim2.newrev(rev, mark=False)
    assert newrev == 'rev2'

def test_newrev_4():
    rev = 'Xrev4'
    newrev = sim2.newrev(rev, mark=True)
    assert newrev == 'Xrev5'


# Test random_build function
# ========================== 
class TestRandomBuild(object):
    def test_one_random_build1(self):
        """Test one random build"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 0, 0, seed=1)
        assert ('pak0.test', 'fail') in flipped_tests
        assert ('pak0', 'Xrev2') in changed_paks

    def test_one_random_build_with_pkg_noise(self):
        """Test one random build with pkg noise"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, pkg_noise=100, test_noise=0, seed=2)
        assert set(changed_paks) == set([('pak0', 'rev2'),
                                         ('pak1', 'rev1'),
                                         ('pak2', 'rev1'),
                                         ('pak3', 'rev2'),
                                         ('pak4', 'Xrev2')])

    def test_one_random_build_with_test_noise(self):
        """Test one random build with pkg noise"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        _, flipped_tests = sim2.random_build(
            modules, tests, pkg_noise=0, test_noise=100, seed=2)
        assert set(flipped_tests) == set([('pak0.test', 'fail'),
                                          ('pak1.test', 'pass'),
                                          ('pak2.test', 'pass'),
                                          ('pak3.test', 'fail'),
                                          ('pak4.test', 'fail')])


    def test_random_build_with_pkg_and_test_noise(self):
        """Test a build with random noise"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, pkg_noise=100, test_noise=100, seed=2)

        assert changed_paks == [('pak0', 'rev2'),
                                ('pak1', 'rev1'),
                                ('pak2', 'rev1'),
                                ('pak3', 'rev2'),
                                ('pak4', 'Xrev2')]
        assert flipped_tests == [('pak0.test', 'fail'),
                                 ('pak1.test', 'pass'),  #xfail
                                 ('pak2.test', 'pass'),
                                 ('pak3.test', 'fail'),  #randfail
                                 ('pak4.test', 'fail')]

    def test_one_random_build_produces_correct_correlation(self):
        """Test that a random build truly changes both package and its test"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 2, 2)

        pakname = [pak[0] for pak in changed_paks if pak[1] == 'Xrev2']
        testname = [test[0] for test in flipped_tests if test[1] == 'fail' and
                    test[0].strip('.test') == pakname[0]]
        assert pakname
        assert testname

        assert pakname[0] == testname[0].strip('.test')

    def test_two_random_builds(self):
        """Test that two random builds with same seed are the fucking same"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 2, 2, seed=2)

        changed_paks2, flipped_tests2 = sim2.random_build(
            modules, tests, 2, 2, seed=2)

        assert changed_paks == changed_paks2
        assert flipped_tests == flipped_tests2


    def test_same_seed_always_produces_same_result(self):
        """Test that the same seed always produces the same fucking result in
        python3"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 2, 2, seed=2)

        assert set(changed_paks) == set([
            ('pak0', 'rev1'),
            ('pak1', 'rev1'),
            ('pak2', 'rev1'),
            ('pak3', 'rev1'),
            ('pak4', 'Xrev2')]
        )

        changed_paks2, flipped_tests2 = sim2.random_build(
            modules, tests, 2, 2, seed=2)

        assert set(changed_paks) == set([
            ('pak0', 'rev1'),
            ('pak1', 'rev1'),
            ('pak2', 'rev1'),
            ('pak3', 'rev1'),
            ('pak4', 'Xrev2')]
        )

        changed_paks3, flipped_tests3 = sim2.random_build(
            modules, tests, 0, 0, seed=3)

        assert set(changed_paks3) == set([
            ('pak1', 'Xrev2'),
            ('pak3', 'rev1'),
            ('pak2', 'rev1'),
            ('pak0', 'rev1'),
            ('pak4', 'rev1')]
        )


    def test_consecutive_random_does_not_alter_lists(self):
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        mod_len = len(modules)
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]
        test_len = len(tests)

        # First round
        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 0, 0, seed=1)

        assert len(modules) == mod_len  # make sure external list is not changed
        assert len(tests) == test_len

        # Second round
        changed_paks, flipped_tests = sim2.random_build(
            changed_paks, flipped_tests, 0, 0, seed=3)
        assert len(modules) == mod_len  # make sure external list is not changed
        assert len(tests) == test_len

    def test_consecutive_random_build_no_noise(self):
        """Test consecutive random builds"""
        modules = [('pak{}'.format(num), 'rev1') for num in range(5)]
        tests = [('{}.test'.format(pak[0]), 'pass') for pak in modules]

        # First round
        changed_paks, flipped_tests = sim2.random_build(
            modules, tests, 0, 0, seed=1)

        # Second round
        changed_paks, flipped_tests = sim2.random_build(
            changed_paks, flipped_tests, 0, 0, seed=3)
        assert set(changed_paks) == set([('pak0', 'Xrev2'),
                                         ('pak1', 'Xrev2'),
                                         ('pak2', 'rev1'),
                                         ('pak3', 'rev1'),
                                         ('pak4', 'rev1')])
        assert set(flipped_tests) == set([('pak0.test', 'fail'),
                                          ('pak1.test', 'fail'),
                                          ('pak2.test', 'pass'),
                                          ('pak3.test', 'pass'),
                                          ('pak4.test', 'pass')])

        # Third round
        changed_paks, flipped_tests = sim2.random_build(
            changed_paks, flipped_tests, 0, 0, seed=5)
        assert set(flipped_tests) == set([('pak0.test', 'fail'),
                                          ('pak1.test', 'fail'),
                                          ('pak2.test', 'pass'),
                                          ('pak3.test', 'fail'),
                                          ('pak4.test', 'pass')])
        assert set(changed_paks) == set([('pak0', 'Xrev2'),
                                         ('pak1', 'Xrev2'),
                                         ('pak2', 'rev1'),
                                         ('pak3', 'Xrev2'),
                                         ('pak4', 'rev1')])

