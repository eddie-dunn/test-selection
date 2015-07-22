"""Fast generation of test results for package changes"""
# TODO: most tests should have a result for fail/pass -- only some should
# be of unknown state (and correspondingly ignored by the Difference Engine
# Fix this in the random_build() function

from random import Random
import random

from util.util import Build
from util.util import BuildSet
import util.util as util

# Default package name root
PKG_PREFIX = 'pak'

# Default test suffix
TEST_SUFFIX = '.test'

# Default rev suffix
REV_PREFIX = 'rev'
REV_DEFAULT = 'rev1'

# Test statuses
TEST_STATUS = ('pass', 'fail')

def newrev(rev, mark):
    """Intelligently increment revision. Adding mark if mark == True"""
    if mark and not rev.startswith('X'):
        new_rev = "{}{}".format("X", util.increment(rev))
    elif not mark and rev.startswith('X'):
        new_rev = util.increment(rev[1:])
    else:
        new_rev = util.increment(rev)
    return new_rev


def _testnoise2(tests_dict, tests, test_noise, seed):
    # TODO Test me!
    # If test_noise, add some randomy flipped tests
    change = Random().random()
    if change < test_noise/100.0:
        nbr_to_change = 2
        randomly_change_tests = Random(seed).sample(tests, nbr_to_change)
        for test in randomly_change_tests:
            # note to prevent possible bugs I should remove the changed tests
            # from the modules list. it is not currently necessary, however
            _testname = test[0]
            _teststatus = test[1]
            tests.remove((_testname, _teststatus))
            tests_dict[_testname] = ('pass' if _teststatus == 'fail' else 'fail')


def _testnoise(tests_dict, tests, test_noise, seed):
    # If test_noise, add some randomy flipped tests
    randomly_change_tests = Random(seed).sample(tests, test_noise)
    for test in randomly_change_tests:
        # note to prevent possible bugs I should remove the changed tests from
        # the modules list. it is not currently necessary, however
        _testname = test[0]
        _teststatus = test[1]
        tests.remove((_testname, _teststatus))
        tests_dict[_testname] = ('pass' if _teststatus == 'fail' else 'fail')


def _pkgnoise2(paks_dict, modules, pkg_noise, seed):
    # TODO Test me!
    # If test_noise, add some randomy flipped tests
    change = Random().random()
    if change < pkg_noise/100.0:
        nbr_to_change = 2
        randomly_change_pkgs = Random(seed).sample(modules, nbr_to_change)
        for pkg in randomly_change_pkgs:
            # note to prevent possible bugs I should remove the changed tests from
            # the modules list. it is not currently necessary, however
            _pkgname = pkg[0]
            _revname = pkg[1]
            modules.remove((_pkgname, _revname))
            paks_dict[_pkgname] = newrev(_revname, mark=False)


def _pkgnoise(paks_dict, modules, pkg_noise, seed):
    randomly_change_pkgs = Random(seed).sample(modules, pkg_noise)
    for pkg in randomly_change_pkgs:
        # note to prevent possible bugs I should remove the changed pkgs from
        # the modules list. it is not currently necessary, however
        _pkgname = pkg[0]
        _revname = pkg[1]
        modules.remove((_pkgname, _revname))
        paks_dict[_pkgname] = newrev(_revname, mark=False)


def add_noise(paks_dict, tests_dict, modules, tests, pkg_noise, test_noise,
              seed):
    """Function to add noise to build

    """
    # If pkg_noise, add some randomly changed packages
    _pkgnoise2(paks_dict, modules, pkg_noise, seed)

    # If test_noise, add some randomy flipped tests
    _testnoise2(tests_dict, tests, test_noise, seed)


def _choice(seq, seed):
    """Choose a random element from a non-empty sequence.

    Embedding random.choice from 2.6 in order to get an uniform
    results between 2.6 and 3.2, where random module has been
    changed because of http://bugs.python.org/issue9025.
    See also http://groups.google.com/group/comp.lang.python\
    /browse_thread/thread/2b000b8ca8c5e98e

    Credit:
        https://mail.python.org/pipermail/python-list/2012-February/632219.html

    Raises IndexError if seq is empty
    """
    rng = random.Random(seed)
    return seq[int(rng.random() * len(seq))]


def random_build(modules, tests, pkg_noise, test_noise, seed=None):
    """Generate a build with random changes to packages.

    This function will generate a build with the following behavior:

        * Include true correlated changes, meaning a package change that causes a
    test flip.
        * Optionally add some package change noise
        * Optionally add some test flip noise (to simulate, e.g. "blinking"
          tests)

    Args:
        mappings (dict): A dictionary that contains the true mappings between a
            package name and (a) testname(s)
        old_build (Build): A previous build, used to determine the correct
            values for changed packages and test flips
        pkg_noise (int): Amount of extra (non-correlated) package changes to
            add tot he build.
        test_noise (int): Amount of extra (non-correlatd) test flips to add
            to the build.
        seed (int?): Only use this to produce determinstic resulst (i.e. for
            unit testing purposes).

    Returns:
        tuple of lists: (changed_packages, flipped_tests)

    """
    # Preparations
    paks_dict = dict(modules)
    tests_dict = dict(tests)
    modules = modules[:]  # copy so external list is not changed
    tests = tests[:]  # copy so external list is not changed

    # Get the packages to change for this build
    # TODO Change variable nbr of packages
    change_pkg = _choice(modules, seed)
    modules.remove(change_pkg)
    pakname = change_pkg[0]
    # print(pakname)

    paks_dict[pakname] = newrev(change_pkg[1], mark=True)

    # Flip the test belonging to the package
    testname = "{}.test".format(pakname)

    prev_status = tests_dict[testname]
    tests.remove((testname, prev_status))
    test_status = ('pass' if prev_status == 'fail' else 'fail')
    tests_dict[testname] = test_status

    # Add pkg and test noise, if applicable
    add_noise(paks_dict, tests_dict, modules, tests, pkg_noise, test_noise,
              seed)

    # Convert dicts back to lists
    ret_tests = sorted([(k, v) for k, v in tests_dict.items()])
    ret_paks = sorted([(k, v) for k, v in paks_dict.items()])
    return ret_paks, ret_tests


def random_choice(modules, seed=None):
    return Random(seed).choice(modules)


def generate_buildset(size, mappings, pkg_noise=0, test_noise=0, seed=None):
    """Generate a buildset of size `size`.

    Args:
        size (int): Size of buildset
        mappings (dict): Dict mapping pkgnames (keys) to testnames (values)
        seed (int): The seed used for randomized values

    Returns:
        buildset (BuildSet): An object containing several builds

    """
    buildset = BuildSet()

    available_test_names = sorted(list(mappings.values()))
    tests = []
    for name in available_test_names:
        tests.append((name, TEST_STATUS[0]))

    available_pkg_names = sorted(list(mappings.keys()))
    pkgs = []
    for name in available_pkg_names:
        pkgs.append((name, 'rev0'))

    for buildnbr in range(size):
        pkgs, tests = random_build(pkgs, tests,
                                    pkg_noise=pkg_noise,
                                    test_noise=test_noise, seed=seed)
        new_build = Build(buildnbr, pkgs, tests)
        buildset.add(new_build)

    return buildset


def generate_pkg_names(nbr, prefix='pak'):
    """Generate a list of package names"""
    return ["{}{}".format(prefix, num) for num in range(nbr)]


def pkgmappings(pkgnames, test_suffix='.test'):
    """Generate a dict with pkgnames as keys and testnames as values"""
    mappings = {pak: "{}{}".format(pak, test_suffix) for pak in pkgnames}
    return mappings

# pylint: disable=too-many-arguments
def create_superset(products=1, packages=10, builds=2, pkg_noise=0,
                    test_noise=0, seed=None):
    """Create several sets of builds with package changes and test flips so
    that the Difference Engine can analyze it."""
    prod_list = []
    for num in range(products):
        prod_list.append('prod{}'.format(num))

    pkg_names = generate_pkg_names(packages)
    pkg_mappings = pkgmappings(pkg_names)

    superset = {}
    for product in prod_list:
        buildset = generate_buildset(
            builds, pkg_mappings, pkg_noise=pkg_noise,
            test_noise=test_noise, seed=seed)
        superset[product] = buildset.dict

    return superset

