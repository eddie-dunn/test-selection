"""Utility functions and stuff"""
import time
import logging
import json
import re
from collections import OrderedDict

# http://www.kammerl.de/ascii/AsciiSignature.php
# http://www.network-science.de/ascii/


# util functions
# ==============
#        _   _ _    __                  _   _
#       | | (_) |  / _|                | | (_)
#  _   _| |_ _| | | |_ _   _ _ __   ___| |_ _  ___  _ __  ___
# | | | | __| | | |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |_| | |_| | | | | | |_| | | | | (__| |_| | (_) | | | \__ \
#  \__,_|\__|_|_| |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
def timeit(method):
    """Use to decorate functions/methods to log how long they take
    TODO: Disable timed if logging info is not enabled"""
    def timed(*args, **kwargs):  # pylint:disable=missing-docstring
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        logging.info("function %s took %.3f sec", method.__name__, end-start)
        return result
    # Only time if log level is high enough
    return timed


def set_default(obj):
    """Used for json.dumps to deal with set objects"""
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def hashable(iterable):
    """Convert elements in iterable to tuples"""
    return [tuple(item) for item in iterable]


def json_loads(string):
    """A custom json load string function is needed in order to make sure that
    the order is preserved.

    Args:
        string (str): JSON serializable string

    Returns:
        (dict): An ordered dict with json data
    """
    return json.loads(string, object_pairs_hook=OrderedDict)


def assert_is_ordered(container):
    """Make sure we are dumping ordered content"""
    if not isinstance(container, OrderedDict):
        raise TypeError("Container needs to be OrderedDict but was "
                        "{}".format(type(container)))


def json_dumps(content, pretty=False, assert_ordered=False):
    """Create a json string from iterable. If `pretty` == True, it will be
    human readable"""
    if assert_ordered:
        for product in content:
            assert_is_ordered(content[product])

    if pretty:
        return json.dumps(content, indent=4, separators=(',', ': '))
    return json.dumps(content)


def is_list_or_set(item):
    """Returns True if item is set or list"""
    if isinstance(item, set) or isinstance(item, list):
        return True
    return False


def is_tuple_or_list(item):
    """Returns True if item is a tuple"""
    if isinstance(item, type(())) or isinstance(item, list):
        return True
    return False


def validate_list_or_set(iterable):
    """Validate iterable to be either a list or set of tuples"""
    if not is_list_or_set(iterable):
        raise TypeError("Iterable not valid list or set, was "
                        "{}".format(type(iterable)))

    if iterable == []:  # If iterable is empty list it is also valid
        return

    first_item = next(iter(iterable))
    if not is_tuple_or_list(first_item):
        raise TypeError("Expected tuple, found {} in {} of {}".format(
            type(first_item), type(iterable), list(iterable)[:3]))


def validate_build_contents(*build_contents):
    """Takes a variable list of parameters and verifies that they are a list or
    set of tuples or lists"""
    for item in build_contents:
        validate_list_or_set(item)


def increment(string):
    """Look for the last sequence of number(s) in a string and increment
    Source:
   http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/#c1
    """
    last_num = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
    reg_m = last_num.search(string)
    if reg_m:
        next_val = str(int(reg_m.group(1))+1)
        start, end = reg_m.span(1)
        incremented_string = (string[:max(end-len(next_val), start)] +
                              next_val + string[end:])
    return incremented_string


def get_names(list_of_tuples):
    """From a list or similar iterable, where each item contains a tuple,
    return the first element in the tuple. E.g:
    get_names([('name', 'extra'), ('name2', 'x')]) == ['name', 'name2']

    Args:
        list_of_tuples (iterable): An iterable containing the name/data pairs

    Returns:
        list: A list of the names from the name/data pairs
    """

    try:
        names = dict(list_of_tuples).keys()
    except ValueError:
        names = []
    return list(names)

# ______       _ _     _   _____ _
# | ___ \     (_) |   | | /  __ \ |
# | |_/ /_   _ _| | __| | | /  \/ | __ _ ___ ___  ___  ___
# | ___ \ | | | | |/ _` | | |   | |/ _` / __/ __|/ _ \/ __|
# | |_/ / |_| | | | (_| | | \__/\ | (_| \__ \__ \  __/\__ \
# \____/ \__,_|_|_|\__,_|  \____/_|\__,_|___/___/\___||___/
# Build Classes


class BaseBuild(object):
    """A base class for a Build object"""

    module_string = 'modules'
    test_string = 'tests'

    def __init__(self, name, packages, tests):
        self.name = str(name)
        self.packages = list(packages)
        self.tests = list(tests)

    @property
    def dict(self):
        """Return Build as a dict"""
        tup = ((self.module_string, sorted(self.packages)),
               (self.test_string, sorted(self.tests)))
        ordered = OrderedDict(tup)
        mdict = OrderedDict()
        mdict[self.name] = ordered
        return mdict

    def json(self, indent=False):
        """Return Build as a json entity"""
        mdict = self.dict
        if indent:
            return json.dumps(mdict, default=set_default, indent=indent)
        else:
            return json.dumps(mdict, default=set_default)

    def __str__(self):
        return self.json(indent=True)

    def __repr__(self):
        return self.json()

    @classmethod
    def build_from_dict(cls, name, contents):
        """Create a Build from a dict"""
        modules = contents['modules']
        tests = contents['tests']
        return cls(name, modules, tests)


class Build(BaseBuild):
    """A build object contains the packages that were changed in a build as
    well as the tests which failed (or perhaps flipped, to be decided)"""

    def __init__(self, name, packages=None, tests=None):
        """Create a new build.

        Args:
            name (str): Name of build
            packages (iterable): An iterable of tuples or lists of the format
            ('pkgname', 'revnum')
            tests (iterable): An iterable containing tuples or lists of the
            format ('testname', 'teststatus')
        """
        if not packages:
            packages = []
        if not tests:
            tests = []

        # Assert that the correct objects are passed to the constructor
        # TODO: Fix validation after optimization is done...
        validate_build_contents(packages, tests)
        super(Build, self).__init__(name, packages, tests)

    def has_test(self, test):
        """Returns true if `test` exists set"""
        return test in [_test[0] for _test in self.tests if _test]

    def has_package(self, package):
        """Returns true if `package` exists in set"""
        return package in [pkg[0] for pkg in self.packages if pkg]

    @classmethod
    def _diff_list(cls, first, second):
        """Diff between first and second (list or set of tuples)"""
        diff = set(hashable(first)) - set(hashable(second))
        return {mod[0] for mod in diff if mod}
        # eTODO: Should seriously consider returning a list instead of a set
        # since this guarantees the order of stuff when saving as json
        # return sorted([mod[0] for mod in diff if mod])

    def __sub__(self, other):
        """Use function _diff_list to calculate the difference between packages
        and tests"""
        mod_diff = self._diff_list(self.packages, other.packages)
        test_diff = self._diff_list(self.tests, other.tests)
        diff = {self.module_string: mod_diff, self.test_string: test_diff}
        return diff


class BuildSet(object):
    """An ordered set of Builds"""

    def __init__(self, builds=None, product='none'):
        self.product = product
        self._builds = builds or list()

    def add(self, build):
        """Add build to buildset"""
        self._builds.append(build)

    @property
    def size(self):
        """Return size of BuildSet"""
        return len(self._builds)

    @property
    def builds(self):
        """Return buildset"""
        return self._builds

    @property
    def dict(self):
        """Return BuildSet as an ordered dict"""
        mdict = OrderedDict()
        for build in self.builds:
            # mdict[build.name] = build.dict[build.name]
            mdict.update(build.dict)

        return mdict

    @classmethod
    def from_string(cls, string):
        """Create a BuildSet from a text string."""
        mdict = OrderedDict(json_loads(string))
        builds = []
        for build in mdict:
            builds.append(Build.build_from_dict(build, mdict[build]))
        return BuildSet(builds=builds)

    def json(self, indent=None):
        """Convert buildset to json"""
        # return json.dumps(self.dict, indent=indent, separators=(',', ': '))
        return json_dumps(self.dict, pretty=indent)

    def __str__(self):
        return self.json()
