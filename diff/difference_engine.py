# -*- coding: utf-8 -*-
""" Difference Engine™

TODO: Update documentation

This module implements the Difference Engine™. Given the input of code packages
and test pacakges it will produce the correlations between tests and code as
output.

Input:
    A series of Builds. A Build is a combination of changed packages and test
    results. A series of Builds is the data you want to run the analysis on. It
    is not required that the same packages are changed for every Build in the
    series, or that the same tests are affected, but some appropriate filtering
    of the data *is* required, or the Difference Engine won't be able to
    produce meaningful results.

Output:
    A mapping between test cases and code packages contained inside the series
    of Builds.


The Difference Engine™ looks at differences between test outcomes for each
package. That is, if a change is made to package A and test A1 fails when it
succeeded in a previous step, the mapping A->A1 will get 1 point. If a change
is then subsequently made to package A and test A1 succeeds, A->A1 will get
another point. Conversely, if package A is changed and A1 keeps failing, no
point will be given. It is the change from success->failure or failure->success
that awards points.

Note that the order of the Builds therefore is important.

Implementation wise, the set of builds is a list made of dicts:

        buildset = []
        build1 = {'changed': ["A", "B", "C"],
                  'failed': ["A1", "B1", "C1", "D1"]}
        buildset.append(build1)

Where the 'changed' and 'failed' keywords contain the changed packages and the
failed tests respectively.


The analyzed results are put in a dict with the following structure:

    pkgdb = {'pak1': {'testA': {'correlation': 3, 'last_outcome': 'fail'},
                      'testB': {'correlation': 1, 'last_outcome': 'pass'},
                      'test8': {'correlation': 9, 'last_outcome': 'fail'},
                     }
             'pak4': {'testA': {'correlation': 7, 'last_outcome': 'fail'},
                      'test8': {'correlation': 9, 'last_outcome': 'fail'},
                     }
            etc...
    }

This module also contains a method to print the analyzed results, showing how
much each test depends on each package.
"""
# TODO: Update docstring

# External imports
from __future__ import print_function
import logging
import copy
import operator
from collections import OrderedDict

# Internal imports
import util.util as util
#from diff.util import timeit
from util.util import hashable
from util.util import json_loads
from util.util import validate_build_contents


def changed_modules(prev_build, next_build):
    """Returns the modules in next_build that have changed since prev_build.

    A Build is a dict that must contain the key `modules`. Build['modules']
    contains a list of module names and their revisions.

    Args:
        prev_build (dict): The previous Build, e.g:
            prev_build = {'modules': [('mod1', 'rev1'), ('mod2', 'rev1')]}
        next_build (dict): The current Build, e.g:
            next_build = {'modules': [('mod1', 'rev2'), ('mod2', 'rev1')]}

    Returns:
        (list) A list of module names that were changed between prev_build and
        next_build. Continuing the example above, the returned list will be:

            ['mod1']
    """
    # The function `hashable` is used to convert lists to tuples, if applicable
    modules_prev = set(hashable(prev_build['modules']))
    modules_next = set(hashable(next_build['modules']))
    changed = modules_next - modules_prev
    return [mod[0] for mod in changed]


def rm_params_from_names(mlist):
    """Look at testnames and filter out everything after a '(' character, to
    avoid different names for testnames that include parameters.

    Args:
        mlist (list): A list containing tests and their status, e.g:
            [('list(param1, param2)', 'pass'),
             ('of', 'fail'),
             ('tests(foo, bar)', 'pass')]

    Returns:
        (list): A list of tests and their status, with everything after the
        rightmost `(` filtered out. E.g:
            [('list, 'pass'),
             ('of', 'fail'),
             ('tests', 'pass')]
    """
    return [(name[0][:name[0].rfind('(')], name[1])
            if '(' in name[0]
            else name for name in mlist]


def flips(prev_build, next_build):
    """Returns the tests in next_build that have flipped since prev_build.
    I.e. this diff will return a set with test elements in next_build that are
    different from the elements in prev_build.

    A Build must contain the key `tests`, pointing to a list of failed tests.

    Args:
        prev_build (dict): The previous Build, e.g:
            prev_build = {'tests': [('test1', 'pass'), ('test2', 'fail'),
                                    ('testX', 'pass')]
        next_build (dict): The current Build, e.g:
            next_build = {'tests': [('test1', 'fail'), ('testY', 'pass')]

    Returns:
        (list) A list of module names that were changed between prev_build and
        next_build. Continuing the example above, the returned list will be:

            ['test1', 'testY']
    """
    tests_prev = rm_params_from_names(prev_build['tests'])
    tests_next = rm_params_from_names(next_build['tests'])
    validate_build_contents(tests_prev, tests_next)
    tests_prev_set = set(hashable(tests_prev))
    tests_next_set = set(hashable(tests_next))
    diff = tests_next_set - tests_prev_set
    name_intersect = (set(util.get_names(tests_prev_set)) &
                      set(util.get_names(tests_next_set)))
    return [test[0] for test in diff if test[0] in name_intersect]


#@timeit
def diff_builds(buildset, pkgnames=None, testnames=None):
    """Iterate through BuildSet and find which packages were changed in
    subsequent builds, and which tests flipped. It is very important that
    buildset is ordered. Unchanged packags will be removed from the return
    dict. Tests that have not flipped will be removed from the return dict.

    Args:
        buildset (dict OR BuildSet): A dict containing several builds, in
        order. E.g.:
        {'prod': OrderedDict(
            'bid1':
                'modules': [(module1, rev_id), (module2, rev_id)]
                'tests': [list of (testname, teststatus)]
            'bid2':
                'modules': [(module1, rev_id), (module2, rev_id)]
                'tests': [list of (testname, teststatus)]
            )
         'prod2': OrderedDict(
            'bid1':
                'modules': [(module1, rev_id), (module2, rev_id)]
                'tests': [list of (testname, teststatus)]
            'bid2':
                'modules': [(module1, rev_id), (module2, rev_id)]
                'tests': [list of (testname, teststatus)]
            )
        }

    Returns:
        ret (list): A list containing several builds, in order. E.g:
        [
            {'modules': [list of changed modules]
            'tests': [list of FLIPPED tests]},
            {'modules': [list of changed modules]
            'tests': [list of FLIPPED tests])},
            {'modules': [list of changed modules]
            'tests': [list of FLIPPED tests]},
            {'modules': [list of changed modules]
            'tests': [list of FLIPPED tests]},
        ]
        This list will be used to calculate correlations later

    """
    def assert_ordered(item):
        """Makes sure item is an OrderedDict"""
        if not isinstance(item, OrderedDict):
            raise TypeError("You MUST diff an ordered dictionary, but was "
                            "{}".format(type(item)))

    ret = []

    for product in buildset:
        assert_ordered(buildset[product])  # must be OrderedDict
        prev_build = None
        for buildname in buildset[product]:
            current_build = buildset[product][buildname]
            # Add pkg/test names to corresponding sets if applicable
            if isinstance(pkgnames, set) and isinstance(testnames, set):
                testnames.update(set(dict(current_build['tests'])))
                pkgnames.update(set(dict(current_build['modules'])))

            # initialize build -1 to the same as the first build
            if not prev_build:
                prev_build = current_build
            module_diff = changed_modules(prev_build, current_build)
            test_diff = flips(prev_build, current_build)
            # append _sorted_ diffs to make comparisons easier
            # NOTE if this sorting takes too long, revert to using sets
            ret.append({'modules': sorted(module_diff),
                        'tests': sorted(test_diff)})
            prev_build = current_build

    return ret


#@timeit
def correlate(diff_list):
    """Go through the list of changed modules and flipped tests and count the
    correlations.

    Args:
        diff_list (list): A list containing changed modules and the tests that
        flipped when said modules were changed. E.g:

        diff1 = [
            {'modules': ['mod1', 'mod2'],
            'tests': ['testA', 'testB', 'testC']},
            {'modules': ['mod1', 'mod3'],
            'tests': ['testA', 'testC']},
        ]

    Return:
        correlation (dict): A dict containing modules, the tests that are
        correlated with them, and the module-to-test correlation weights. E.g:

        correlation = {
            'mod1': {'testA': 2, 'testB': 1, 'testC': 2},
            'mod2': {'testA': 1, 'testB': 1, 'testC': 1},
            'mod3': {'testA': 1, 'testB': 0, 'testC': 1}
        }

    """
    def increment_correlation(ordered_dict, module, test):
        """Increment correlation for module and test in ordered_dict"""
        # the try-except dance is performed in case the module or test key has
        # not been initialized yet
        try:
            ordered_dict[module]
        except KeyError:
            ordered_dict[module] = OrderedDict()
        try:
            ordered_dict[module][test]
        except KeyError:
            ordered_dict[module][test] = 0
        ordered_dict[module][test] += 1

    correlations = OrderedDict()
    for diff in diff_list:
        for module in diff['modules']:
            for test in diff['tests']:
                increment_correlation(correlations, module, test)

    return correlations


def diff_json(json_string):
    """Placeholder function to replace parse_json function"""
    return parse_json(json_string)


def parse_json(json_string):
    """Use when indata is in the form of json"""
    build_superset = json_loads(json_string)  # create dict from json text
    diff = diff_builds(build_superset)
    return diff


# Main method stuff
# #################

#@timeit
def filter_correlations(diff, cutoff=-1):
    """Filter (remove) unwanted entries from database"""
    retdb = copy.deepcopy(diff)
    for pak in diff:
        for test in diff[pak]:
            if diff[pak][test] < cutoff:
                del retdb[pak][test]
                if retdb[pak] == {}:
                    del retdb[pak]
        if diff[pak] == {}:
            del retdb[pak]

    logging.debug("filtered dict: %s", retdb)
    return retdb

#@timeit
def printable_analysis(correlation, cutoff=-1):
    """Returns a print-friendly list based on the input database"""
    # Filter out correlations below cutoff limit:
    data = filter_correlations(correlation, cutoff=cutoff)

    output = []
    for pak in sorted(data):
        output.append(pak)  # Add package name to output

        # sort test results with highest weight first, if weight is same, sort
        # by testname
        test_results = sorted(
            data[pak].items(), key=operator.itemgetter(1, 0), reverse=True)

        # Add test results to output list
        for test in test_results:
            test_weight = test[1]
            test_name = test[0]
            output.append('  %s:\t%s' % (test_name, test_weight))

    return output
