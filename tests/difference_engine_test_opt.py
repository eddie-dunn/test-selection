"""Tests for difference engine"""
import diff.difference_engine as difference_engine
import unittest
from collections import OrderedDict
from diff.difference_engine import parse_json
from diff.difference_engine import correlate

# pylint:disable=missing-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=bad-whitespace,invalid-name
# pylint: disable=no-self-use


def test_correct_correlations():
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
    build_text = """
             {"product": {
                  "bid1": {
                       "modules": [
                               ["pakX", 1], ["pak2", 1]
                       ],
                       "tests": {
                           "pass": [
                                "testX"
                            ],
                            "fail": [
                                "test1"
                            ]
                       }
                  },
                  "bid2": {
                       "modules": [
                               ["pakX", 2], ["pak2", 2]
                       ],
                       "tests": {
                           "pass": [
                                "test1"
                            ],
                            "fail": [
                                "testX"
                            ]
                       }
                  },
                  "bid3": {
                       "modules": [
                               ["pakX", 2], ["pak2", 1]
                       ],
                       "tests": {
                           "pass": [
                                "testX"
                            ],
                            "fail": [
                                "test1"
                            ]
                       }
                  },
                  "bid4": {
                       "modules": [
                               ["pakX", 3], ["pak2", 3]
                       ],
                       "tests": {
                           "pass": [
                                "test1"
                            ],
                            "fail": [
                            ]
                       }
                  }
                }
             }
             """
    diff = parse_json(build_text)
    correlation = correlate(diff)
    correct_correlation = {'pak2': {'test1': 3, 'testX': 2},
                           'pakX': {'test1': 2, 'testX': 1}}
    assert correlation == correct_correlation


def test_filter_test_params():
    mlist = ['list',
             'of',
             'stuff',
             'with(1, foo, bar, baz)',
             'some',
             'params(foo, bar']
    correct_list = ['list',
                    'of',
                    'stuff',
                    'with',
                    'some',
                    'params']
    filtered = difference_engine.rm_params_from_names(mlist)
    assert filtered == correct_list


class ParseJSON(unittest.TestCase):
    """
    Initializes text strings containing JSON-structures that includes a product
    with corresponding builds, modules, and tests (and their results)
    """
    # pylint: disable=invalid-name
    def setUp(self):
        self.text_big = """
            {"product1": {
                "56577": {
                    "modules": [
                        [
                            "packages/web/apps/cgiprg/logger",
                            "292a05517750d75db1beb59b6c8d292d6c202902"
                        ],
                        [
                            "libs/freetype2",
                            "fdbe9db5c652921af2153a2e3ef33f0a54d22c4a"
                        ],
                        [
                            "packages/initscripts/iptables-filter-input",
                            "124b4561d4ba5a53afafa25e3399ab22f9c732ad"
                        ],
                        [
                            "apps/utils/root_wrapper",
                            "ac4e140afb090fffb8745e6716d19b2f2ac9a04b"
                        ]
                    ],
                    "tests": {
                        "pass": [
                            "libs/freetype2.test",
                            "initscripts/iptables-filter-input.test"
                        ],
                        "fail": [
                            "cgiprg/loggertest",
                            "utils/root_wrapper.test",
                            "test_will_pass_next_time"
                        ]
                    }
                },
                "56578": {
                    "modules": [
                        [
                            "packages/web/apps/cgiprg/logger",
                            "X"
                        ],
                        [
                            "libs/freetype2",
                            "fdbe9db5c652921af2153a2e3ef33f0a54d22c4a"
                        ],
                        [
                            "packages/initscripts/iptables-filter-input",
                            "X"
                        ],
                        [
                            "apps/utils/root_wrapper",
                            "ac4e140afb090fffb8745e6716d19b2f2ac9a04b"
                        ]
                    ],
                    "tests": {
                        "pass": [
                            "cgiprg/loggertest",
                            "libs/freetype2.test",
                            "test_will_pass_next_time"
                        ],
                        "fail": [
                            "initscripts/iptables-filter-input.test",
                            "utils/root_wrapper.test",
                            "test_will_pass_next_time",
                            "new_failed_test"
                        ]
                    }
                }
            }}
        """
        self.text_small = """
            {"prod": {
                 "bid1": {
                            "modules": [
                                ["mod1", "1"],
                                ["mod2", "1"]
                            ],
                            "tests": {
                                "pass":
                                    [
                                        "test2"
                                    ],
                                "fail":
                                    [
                                        "test1"
                                    ]
                            }
                         },
                 "bid2": {
                            "modules": [
                                ["mod1", "1"],
                                ["mod2", "2"]
                            ],
                            "tests": {
                                "pass":
                                    [
                                        "test3"
                                    ],
                                "fail":
                                    [
                                        "test2"
                                    ]
                            }
                }
            }}
        """

    def test_json_loads(self):
        """
        Test that the correct
        """
        loaded = difference_engine.json_loads(self.text_small)
        assert 'test1' in loaded['prod']['bid1']['tests']['fail']
        assert ['mod2', '2'] in loaded['prod']['bid2']['modules']

    def test_parse_json_text_small_correct(self):
        parsed = difference_engine.parse_json(self.text_small)
        correct = [{'modules': [], 'tests': []},
                   {'modules': [u'mod2'], 'tests': ['test2']}]
        assert parsed == correct

    # @pytest.mark.xfail
    def test_parse_json_text_big_flips(self):
        parsed = difference_engine.parse_json(self.text_big)
        assert "test_will_pass_next_time" in parsed[1]['tests']
        assert 'libs/freetype2.test' not in parsed[1]['tests']

    # @pytest.mark.xfail
    def test_parse_json_text_big_changed_modules(self):
        parsed = difference_engine.parse_json(self.text_big)
        assert "packages/web/apps/cgiprg/logger" in parsed[1]['modules']
        assert "apps/utils/root_wrapper" not in parsed[1]['modules']


# Tests for diff_builds
# =====================
class TestDiffBuilds(unittest.TestCase):

    def setUp(self):
        self.builds = {
            "0": {
                "tests": {
                    "pass":
                        [
                            "pak1.test",
                            "pak4.test"
                        ],
                    "fail":
                        [
                            "mod5.test",
                            "pak0.test"
                        ]
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
                    "pass":
                        [
                            "pak1.test",
                            "mod5.test"
                        ],
                    "fail":
                        [
                            "pak4.test",
                            "pak7.test"
                        ]
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
            }}
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


# Tests for flips
# ================
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

    diff1 = [
        # mod3 not changed
        {'modules': ['mod1', 'mod2'], 'tests': ['testA', 'testB', 'testC']},
        # mod2 not changed
        # testB did not flip
        {'modules': ['mod1', 'mod3'], 'tests': ['testA', 'testC']},
        # mod1 not changed
        # testC did not flip
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


# Tests for printable_analysis
# ============================
def test_printable_analysis():
    correlation = {
        'mod1': {'testA': 2, 'testB': 2, 'testC': 3},
        'mod2': {'testA': 2, 'testB': 3, 'testC': 2},
        'mod3': {'testA': 2, 'testB': 2, 'testC': 2}
        }
    printable1 = difference_engine.printable_analysis(correlation)
    printable2 = difference_engine.printable_analysis(correlation, cutoff=3)
    assert 'mod3' in printable1
    # With cutoff at 3, nothing from mod3 should show...
    assert 'mod3' not in printable2


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
