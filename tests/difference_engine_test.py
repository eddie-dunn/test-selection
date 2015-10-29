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


def make_build(pkgset=None, testset=None):
    """Make a build from a pkgset and a testset.

    pkgset (list|tuple): follows the format
        [["mod1, "1"], ["mod2", "1"]]

    testset (dict): follows the format
        { "pass": [ "test2" ], "fail": [ "test1" ] }

    """
    build = {'tests': testset or {},
             'modules': pkgset or {}
            }
    return build

def make_testset(passed=None, failed=None):
    """Takes passed and failed arguments and constructs a testset for a Build.

    passed (list|str): Either a list of strings or a whitespace separated
        string of names
    failed (list|str): Either a list of strings or a whitespace separated
        string of names
    """
    if isinstance(passed, str):
        passed = passed.split()
    if isinstance(failed, str):
        failed = failed.split()
    return {'pass': passed or [], 'fail': failed or []}


class Integration(unittest.TestCase):
    """Integration tests"""
    def test_from_json_to_correlation(self):
        # TODO: Implement this
        pass

class Functional(unittest.TestCase):
    """Functional tests"""

    def test_correlations_are_calculated_correctly(self):
        """Test that flips are correctly calculated

        Assuming only pakX and pak2 exists in db, and with the following
        build order:
                         # Packages + revs           # Failed tests
           [Build('bid1', [('pakX', 1), ('pak2', 1)], ['test1']),
            Build('bid2', [('pakX', 2), ('pak2', 2)], ['testX']),
            Build('bid3', [('pakX', 2), ('pak2', 1)], ['test1']),
            Build('bid4', [('pakX', 3), ('pak2', 3)], ['testX'])]

        Changed packages for each build will be:
        []
        ['pak2', 'pakX']
        ['pak2']
        ['pak2', 'pakX']

        But what is the correct test flip calculation?

        If I take the symmetric difference, it will be:
        []
        ['test1', 'testX']
        ['test1', 'testX']
        ['test1', 'testX']

        Giving
        {pak2: test1: 3, testX: 3
         pakX: test1: 2, testX: 2}

        On the other hand, if I take into account the test statuses for a code
        package during the last time said package was changed I would get the
        following correlations:

        {pak2: test1: 3, testX: 3
         pakX: test1: 1, testX: 1}

        Since the test results are identical in bid2 and bid4, pakX doesn't
        get the extra correlation++ it gets with the symmetric difference
        method.

        Should I consider the tests statuses the last time a package was
        changed? This means a different correlation altogether...
        """
        builds = [
            make_build([('pakX', 1), ('pak2', 1)],
                       make_testset(passed='testX', failed='test1')),
            make_build([('pakX', 2), ('pak2', 2)],
                       make_testset(passed='test1', failed='testX')),
            make_build([('pakX', 2), ('pak2', 1)],
                       make_testset(passed='testX', failed='test1')),
            make_build([('pakX', 3), ('pak2', 3)],
                       make_testset(passed='test1', failed=None)),

        ]
        superset = {'prod': OrderedDict(enumerate(builds))}
        diff = difference_engine.diff_builds(superset)
        correlation = difference_engine.correlate(diff)
        correct_correlation = {'pak2': {'test1': 3, 'testX': 2},
                               'pakX': {'test1': 2, 'testX': 1}}
        assert correlation == correct_correlation


def test_print_analysis():
    analysis = {
        'C': {'B1': 2, 'C1': 2, 'A1': 2, 'D1': 2},
        'F': {'B1': 2, 'D1': 2},
        'A': {'B1': 4, 'C1': 2, 'A1': 2, 'D1': 2},
        'D': {'D1': 1},
        'B': {'B1': 3, 'C1': 2, 'A1': 2, 'D1': 1}
    }
    out = difference_engine.printable_analysis(analysis)
    highest_weight_A = int(out[1][-1])
    assert highest_weight_A == 4


class TestDiffBuilds(unittest.TestCase):
    def setUp(self):
        self.builds = {
            "0": {
                "tests": {
                    # ("pak1.test", "pass"),
                    # ("mod5.test", "fail"),
                    # ("pak0.test", "fail"),
                    # ("pak4.test", "pass")
                    'pass': ['pak1.test', 'pak4.test'],
                    'fail': ['mod5.test', 'pak0.test'],
                },
                "modules": [
                    [
                        "pak1",
                        "x"
                    ],
                    [
                        "mod5",
                        4
                    ],
                    [
                        "pak0",
                        "x"
                    ]
                ]
            },
            "1": {
                "tests": {
                    # ("pak1.test", "pass"),
                    # ("mod5.test", "pass"),
                    # ("pak4.test", "fail"),
                    # ("pak7.test", "fail")
                    'pass': ['pak1.test', 'mod5.test'],
                    'fail': ['pak4.test', 'pak7.test'],
                },
                "modules": [
                    [
                        "pak1",
                        "x"
                    ],
                    [
                        "pak0",
                        "x"
                    ],
                    [
                        "mod5",
                        0
                    ]
                ]
            },}
        # The dict has only one package that is changed: mod5
        # and only two tests that have flipped (fail->pass): mod5.test
        #                                      (pass->fail): pak4.test
        ordered_builds = OrderedDict()
        ordered_builds['0'] = self.builds['0']
        ordered_builds['1'] = self.builds['1']

        self.prod = 'prod0'
        self.buildset = {self.prod: ordered_builds}

    def test_diff_builds_raises_error(self):
        with self.assertRaises(TypeError):
            difference_engine.diff_builds({'prod': {'stuff': 'blah'}})

    def test_correct_modules_in_diff_builds(self):
        diff = difference_engine.diff_builds(self.buildset)
        assert 'mod5' in diff[1]['modules']
        assert 'pak1' not in diff[1]['modules']

    def test_correct_type_of_diff_builds(self):
        diff = difference_engine.diff_builds(self.buildset)
        assert isinstance(diff, list)

    def test_correct_tests_in_diff_builds(self):
        diff = difference_engine.diff_builds(self.buildset)
        assert 'pak4.test' in diff[1]['tests']
        assert 'pak1.test' not in diff[1]['tests']

    def test_correct_diff_builds(self):
        diff = difference_engine.diff_builds(self.buildset)
        correct_diff = [
            {'tests': [],
             'modules': []},
            {'tests': ['mod5.test', 'pak4.test'],
             'modules': ['mod5']}
        ]
        assert diff == correct_diff


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
    testset1 = {'pass': ['testA'], 'fail': ['testB']}
    # testset2 = {'pass': ['testB'], 'fail': ['testA']}
    testset2 = make_testset(passed='testB', failed='testA testC')
    build1 = make_build(testset=testset1)
    build2 = make_build(testset=testset2)
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['testA', 'testB'])


def test_flips_are_correct2():
    testset1 = {'pass': ['testA'], 'fail': ['testB']}
    testset2 = {'pass': [], 'fail': ['testA', 'testB']}
    build1 = make_build(testset=testset1)
    build2 = make_build(testset=testset2)
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['testA'])


def test_flips_are_correct3():
    # pylint: disable=line-too-long
    testset1 = {'pass': ['testA'], 'fail': ['testB', 'testC']}
    testset2 = {'pass': ['testC'], 'fail': ['testB', 'testA']}
    build1 = make_build(testset=testset1)
    build2 = make_build(testset=testset2)
    flips = difference_engine.flips(build1, build2)
    assert set(flips) == set(['testA', 'testC'])

# Tests for changed modules
# =========================
def test_diff_modules():
    # build1 and build2 contains modules and their revision id
    build1 = {'modules': [['mod1', 'x'], ('mod2', 'x'), ('mod3', 'y')]}
    build2 = {'modules': [('mod1', 'y'), ('mod2', 'x'), ('mod3', 'x')]}
    correct_changed_modules = ['mod1', 'mod3']
    changed_modules = difference_engine.changed_modules(build1, build2)
    assert set(correct_changed_modules) == set(changed_modules)


def test_correlate():
    # pylint: disable=bad-continuation
    diff1 = [
        # mod3 not changed
        {'modules': ['mod1', 'mod2'], 'tests': ['testA', 'testB', 'testC']},
        # mod2 not changed            # testB did not flip
        {'modules': ['mod1', 'mod3'], 'tests': ['testA', 'testC']},
        # mod1 not changed            # testC did not flip
        {'modules': ['mod2', 'mod3'], 'tests': ['testA', 'testB']},
                                              # testA did not flip
        {'modules': ['mod1', 'mod2', 'mod3'], 'tests': ['testB', 'testC']},
    ]

    correlation = difference_engine.correlate(diff1)

    correct_correlation = {
        'mod1': {'testA': 2, 'testB': 2, 'testC': 3},
        'mod2': {'testA': 2, 'testB': 3, 'testC': 2},
        'mod3': {'testA': 2, 'testB': 2, 'testC': 2}
        }

    assert correlation == correct_correlation


def test_printable_analysis():
    correlation = {
        'mod1': {'testA': 2, 'testB': 2, 'testC': 3},
        'mod2': {'testA': 2, 'testB': 3, 'testC': 2},
        'mod3': {'testA': 2, 'testB': 2, 'testC': 2}
        }
    printable = difference_engine.printable_analysis(correlation, cutoff=3)
    # With cutoff at 3, nothing from mod3 should show...
    assert 'mod3' not in printable
