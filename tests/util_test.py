"""Tests for Util module"""
import util.util as util
from util.util import Build

# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=missing-docstring
# pylint: disable=too-many-public-methods
import unittest
import pytest
from collections import OrderedDict

#  _   _ _   _ _   _____         _
# | | | | | (_) | |_   _|       | |
# | | | | |_ _| |   | | ___  ___| |_ ___
# | | | | __| | |   | |/ _ \/ __| __/ __|
# | |_| | |_| | |   | |  __/\__ \ |_\__ \
#  \___/ \__|_|_|   \_/\___||___/\__|___/
# Random util tests

def test_timeit():
    @util.timeit
    def test_func():
        pass
    test_func()


# Tests for set default
def test_set_default_success():
    assert isinstance(util.set_default({'hej'}), list)


def test_set_default_error():
    with pytest.raises(TypeError):
        util.set_default(['hej'])

# Tests for hashable
def test_hashable():
    iterable = [['list'], ['of'], ['lists']]
    hashable = util.hashable(iterable)
    for item in hashable:
        assert type(item) == tuple

def test_hashable2():
    list_items = [['mod1', 'x'], ['mod2', 'x'], ['mod3', 'y']]
    hashed = util.hashable(list_items)
    list_items_set = [('mod1', 'x'), ('mod2', 'x'), ('mod3', 'y')]
    assert hashed == list_items_set

# Tests for json_loads()
def test_json_loads():
    """Make sure saved items are loaded in order"""
    for _ in range(100):  # Run test 100 times
        string_list = (['"{}": {},'.format(key, value)
                        for key, value in zip(range(5), range(5))])
        string_list.append('"{}": {}'.format('5', '88'))
        string_list.insert(0, "{")
        string_list.append("}")
        string = '\n'.join(string_list)
        loaded = util.json_loads(string)
        count = 0
        for item in loaded:
            assert item == str(count)
            count += 1


# Tests for assert_is_ordered()
def test_assert_is_ordered():
    container = OrderedDict()
    util.assert_is_ordered(container)
    container2 = {}
    with pytest.raises(TypeError):
        util.assert_is_ordered(container2)


# Tests for json_dump()
def test_json_dump():
    container = OrderedDict([('bid1', 1), ('bid2', 2), ('bid3', 3)])
    content = {'prod1': container}
    dump1 = util.json_dumps(content)
    dump2 = util.json_dumps(content, pretty=True)
    assert dump1 == '{"prod1": {"bid1": 1, "bid2": 2, "bid3": 3}}'
    repr_dump2 = ('{\n    "prod1": {\n        "bid1": 1,\n        "bid2": 2,\n'
                  '        "bid3": 3\n    }\n}')
    assert dump2 == repr_dump2


def test_json_dump_assert_ordered():
    container = OrderedDict([('bid1', 1), ('bid2', 2), ('bid3', 3)])
    content = {'prod1': container}
    dump1 = util.json_dumps(content, assert_ordered=True)
    dump2 = util.json_dumps(content, pretty=True)
    assert dump1 == '{"prod1": {"bid1": 1, "bid2": 2, "bid3": 3}}'
    repr_dump2 = ('{\n    "prod1": {\n        "bid1": 1,\n        "bid2": 2,\n'
                  '        "bid3": 3\n    }\n}')
    assert dump2 == repr_dump2


# Test for get_names()

def test_getnames():
    names = util.get_names([('name', 'extra'), ('name2', 'x')])
    assert set(names) == set(['name', 'name2'])


def test_getnames_exception():
    names = util.get_names([()])
    assert names == []


# Tests for increment()
def test_increment():
    string = 'hej ladida204 10'
    incremented = util.increment(string)
    assert incremented == 'hej ladida204 11'


# Build tests
# ===========
# ______       _ _     _   _____         _
# | ___ \     (_) |   | | |_   _|       | |
# | |_/ /_   _ _| | __| |   | | ___  ___| |_ ___
# | ___ \ | | | | |/ _` |   | |/ _ \/ __| __/ __|
# | |_/ / |_| | | | (_| |   | |  __/\__ \ |_\__ \
# \____/ \__,_|_|_|\__,_|   \_/\___||___/\__|___/

class TestBlankBuild(unittest.TestCase):

    def setUp(self):
        self.blank = util.Build('blank')

    def test_subtract_by_blank(self):
        diff = self.blank - util.Build('blank2')
        #assert diff == {'modules': [], 'tests': []}
        assert diff == {'modules': set(), 'tests': set()}

    def test_reverse_subtract_by_blank(self):
        diff = util.Build('blank2') - self.blank
        #assert diff == {'modules': [], 'tests': []}
        assert diff == {'modules': set(), 'tests': set()}

    def test_subtract_by_build(self):
        build = util.Build('b', [('pak1', 'r1')], [('test1', 'pass')])
        diff = self.blank - build
        #assert diff == {'modules': [], 'tests': []}
        assert diff == {'modules': set(), 'tests': set()}

    def test_build_subtract_by_blank(self):
        build = util.Build('b', [('pak1', 'r1')], [('test1', 'pass')])
        diff = build - self.blank
        #assert diff == {'modules': ['pak1'], 'tests': ['test1']}
        assert diff == {'modules': {'pak1'}, 'tests': {'test1'}}


class TestBuild(unittest.TestCase):
    """Tests for the Build class"""

    def setUp(self):
        # Create a minimal build
        self.build = util.Build(
            'build', [('pak1', 'rev1')], [('testFOO', 'fail')])
        self.empty_build = util.Build('empty')

    def test_invalid_params(self):
        with self.assertRaises(TypeError):
            util.Build('n', ['pak'], [()])
        with self.assertRaises(TypeError):
            util.Build('n', [()], ['test'])

    def test_has_test(self):
        assert self.build.has_test('testFOO')
        assert not self.build.has_test('nop')

    def test_has_test_empty_build(self):
        assert not self.empty_build.has_test('testname')

    def test_has_package(self):
        assert not self.build.has_package('pakFOO')
        assert self.build.has_package('pak1')

    def test_has_package_empty_build(self):
        assert not self.empty_build.has_package('pkgname')

    def test_json(self):
        assert self.build.json(indent=4)

    def test_to_string(self):
        assert str(self.build)

    def test_repr(self):
        assert repr(self.build)

    def test_build_to_json(self):
        pkgs = {('pak1', 'rev1'), ('pak2', 'rev1')}
        tests = {('test1', 'pass'), ('test2', 'fail')}
        build = util.Build('name', pkgs, tests)
        assert util.json_loads(build.json())

    def test_build_dict(self):
        pkgs = {('pak1', 'rev1'), ('pak2', 'rev1')}
        tests = {('test1', 'pass'), ('test2', 'fail')}
        build = util.Build('name', pkgs, tests)
        assert 'name' in build.dict
        assert ('pak2', 'rev1') in build.dict['name']['modules']
        assert ('test1', 'pass') in build.dict['name']['tests']

    def test_build_dict_is_ordered(self):
        pkgs = {('pak1', 'rev1'), ('pak2', 'rev1')}
        tests = {('test1', 'pass'), ('test2', 'fail')}
        build = util.Build('name', pkgs, tests)
        util.assert_is_ordered(build.dict)

    # Test Build comparisons
    def test_build_subtraction(self):
        build1_paks = [['pak1', 'rev1'], ['pak2', 'rev1']]
        build1_tests = [['testA', 'fail'], ['testB', 'pass']]
        build1 = Build('build1', build1_paks, build1_tests)

        build2_paks = [['pak1', 'rev2'], ['pak2', 'rev1']]
        build2_tests = [['testA', 'pass'], ['testB', 'fail']]
        build2 = Build('build2', build2_paks, build2_tests)

        diff = build1 - build2
        assert diff == {'modules': {'pak1'}, 'tests': {'testA', 'testB'}}

    def test_build_subtraction_assymetric(self):
        build1_paks = [['pak1', 'rev1'], ['pak2', 'rev1']]
        build1_tests = [['testA', 'fail'], ['testB', 'pass']]
        build1 = Build('build1', build1_paks, build1_tests)

        build2_paks = [['pak1', 'rev2'], ['pak2', 'rev1']]
        build2_tests = [['testA', 'pass'], ['testB', 'fail'],
                        ['testC', 'pass']]
        build2 = Build('build2', build2_paks, build2_tests)

        diff = build1 - build2
        assert diff == {'modules': {'pak1'}, 'tests': {'testA', 'testB'}}

        diff2 = build2 - build1
        assert diff2 == {'modules': {'pak1'},
                         'tests': {'testA', 'testB', 'testC'}}

    def test_sub_for_two_builds1(self):
        build1_tests = [('testA', 'pass'), ('testB', 'fail'), ('testC', 'pass')]
        build2_tests = [('testA', 'fail'), ('testB', 'fail'), ('testC', 'pass')]
        build1 = Build('bid1', [()], build1_tests)
        build2 = Build('bid2', [()], build2_tests)
        diff = build1 - build2
        assert set(diff['tests']) == {'testA'}


    def test_sub_for_two_builds2(self):
        build1_tests = [('testA', 'pass'), ('testB', 'pass'), ('testC', 'pass')]
        build2_tests = [('testA', 'fail'), ('testB', 'fail'), ('testC', 'fail')]
        build1 = Build('bid1', [()], build1_tests)
        build2 = Build('bid2', [()], build2_tests)
        diff = build2 - build1
        assert set(diff['tests']) == {'testA', 'testB', 'testC'}

    def test_sub_with_blank_build1(self):
        build1_tests = [('testA', 'pass'), ('testB', 'pass'), ('testC', 'pass')]
        build1 = Build('bid1', [()], build1_tests)
        build2 = Build('bid2', [()], [()])
        diff = build2 - build1
        assert not diff['tests']

        diff2 = build1 - build2
        assert set(diff2['tests']) == {'testA', 'testB', 'testC'}

    def test_sub_blank_builds(self):
        build1 = Build('bid1', [()], [()])
        build2 = Build('bid2', [()], [()])
        diff = build1 - build2
        assert diff[Build.module_string] == set()
        assert diff[Build.test_string] == set()

    def test_sub_when_same(self):
        build1_tests = [('testA', 'pass'), ('testB', 'pass'), ('testC', 'pass')]
        build_pkgs = [('pak1', 'rev')]
        build1 = Build('bid1', build_pkgs, build1_tests)
        build2 = Build('bid2', build_pkgs, build1_tests)
        diff = build2 - build1
        #assert diff == {Build.module_string: [], Build.test_string: []}
        assert diff == {Build.module_string: set(), Build.test_string: set()}

    # pylint: disable=protected-access
    def test_diff_list_when_same(self):
        list1 = [('pak1', 'rev1')]
        diff = Build._diff_list(list1, list1)
        assert diff == set()

    def test_diff_list_when_blank(self):
        list1 = {()}
        diff = Build._diff_list(list1, list1)
        assert diff == set()

    def test_diff_list_when_first_blank(self):
        list1 = {()}
        list2 = {('stuff',)}
        diff = Build._diff_list(list1, list2)
        assert diff == set()

    def test_build_from_dict(self):
        pak1 = ("p1", "r1")
        test1 = ("p1.test", "fail")
        contents = {"modules": [pak1],
                    "tests": [test1]}
        name = 'bid1'
        build = util.Build.build_from_dict(name, contents)
        assert build.dict == {name: {"modules": [pak1], "tests": [test1]}}

    def test_build_from_dict_fail(self):
        pak1 = "p1"
        test1 = ("p1.test", "fail")
        contents = {"modules": [pak1],
                    "tests": [test1]}
        name = 'bid1'
        with self.assertRaises(TypeError):
            # A Build should check that the modules are not tuples
            util.Build.build_from_dict(name, contents)

        # A BaseBuild does not care to verify that modules are tuples
        assert util.BaseBuild.build_from_dict(name, contents)


# Tests for BuildSet class
# ========================
# ______       _ _     _ _____      _     _____         _
# | ___ \     (_) |   | /  ___|    | |   |_   _|       | |
# | |_/ /_   _ _| | __| \ `--.  ___| |_    | | ___  ___| |_ ___
# | ___ \ | | | | |/ _` |`--. \/ _ \ __|   | |/ _ \/ __| __/ __|
# | |_/ / |_| | | | (_| /\__/ /  __/ |_    | |  __/\__ \ |_\__ \
# \____/ \__,_|_|_|\__,_\____/ \___|\__|   \_/\___||___/\__|___/
#
class TestBuildSet(unittest.TestCase):

    def setUp(self):
        self.build1 = Build(
            'build1',
            {('pak1',), ('pak2',)},
            {('pak1.test',), ('pak2.test',)}
        )
        self.build2 = Build(
            'build2',
            {('pak2',), ('pak3',)},
            {('pak2.test',), ('pak3.test',)}
        )

    def test_BuildSet(self):
        buildset = util.BuildSet()
        buildset.add(self.build1)
        assert self.build1 in buildset.builds
        assert self.build2 not in buildset.builds
        assert buildset.size == 1

    def test_BuildSet_is_ordered(self):
        build3 = util.Build('build3')
        buildset = util.BuildSet([self.build1, self.build2, build3])
        assert isinstance(buildset.dict, OrderedDict)
        keys = list(buildset.dict.keys())
        assert keys == [self.build1.name, self.build2.name, 'build3']

    def test_BuildSet_str(self):
        buildset = util.BuildSet([self.build1, self.build2])
        assert util.json_loads(str(buildset))

    def test_BuildSet_from_string(self):
        set_string = """
            {
                "build1": {
                    "tests": [
                        [
                            "pak1.test", "pass"
                        ],
                        [
                            "pak2.test", "fail"
                        ]
                    ],
                    "modules": [
                        [
                            "pak1", "r1"
                        ],
                        [
                            "pak2", "r1"
                        ]
                    ]
                },
                "build2": {
                    "tests": [
                        [
                            "pak2.test", "pass"
                        ],
                        [
                            "pak3.test", "fail"
                        ]
                    ],
                    "modules": [
                        [
                            "pak2", "r1"
                        ],
                        [
                            "pak3", "r1"
                        ]
                    ]
                }
            }"""
        buildset = util.BuildSet.from_string(set_string)
        assert ['build1', 'build2'] == list(buildset.dict.keys())
        assert 'pak1' in [pakrev[0] for pakrev in
                          buildset.dict['build1']['modules']]
        assert 'pak3' in [pakrev[0] for pakrev in
                          buildset.dict['build2']['modules']]
        assert 'pak2.test' in [test[0] for test in
                               buildset.dict['build2']['tests']]

# Tests for validate_list_or_set()
# ================================
#  _   _       _ _     _       _       _     _     _
# | | | |     | (_)   | |     | |     | |   (_)   | |
# | | | | __ _| |_  __| | __ _| |_ ___| |    _ ___| |_
# | | | |/ _` | | |/ _` |/ _` | __/ _ \ |   | / __| __|
# \ \_/ / (_| | | | (_| | (_| | ||  __/ |___| \__ \ |_
#  \___/ \__,_|_|_|\__,_|\__,_|\__\___\_____/_|___/\__|
class TestValidateListOrSet(unittest.TestCase):
    def test_validate_list_or_set(self):
        validate = util.validate_list_or_set
        validate([('list',), ('of',), ('tuples',)])
        validate({('set', 'of', 'tuples')})
        validate([['list', 'of', 'lists']])

    def test_validate_empty_list(self):
        util.validate_list_or_set([])

    def test_raises_TupleError1(self):
        validate = util.validate_list_or_set
        with self.assertRaises(TypeError):
            validate(['list', 'of', 'stuff'])
        with self.assertRaises(TypeError):
            util.validate_list_or_set(['lo'])

    def test_raises_TupleError2(self):
        validate = util.validate_list_or_set
        with self.assertRaises(TypeError):
            validate({'set', 'of', 'stuff'})

    def test_raises_TypeError(self):
        validate = util.validate_list_or_set
        with self.assertRaises(TypeError):
            validate(1)
        with self.assertRaises(TypeError):
            validate('hi')
        with self.assertRaises(TypeError):
            validate({'key': 'value'})

    def test_is_tuple_or_list(self):
        self.assertTrue(
            util.is_tuple_or_list(('tuple', 'stuff')))
        self.assertTrue(
            util.is_tuple_or_list(['list', 'of', 'stuff']))

    def test_is_not_tuple(self):
        self.assertFalse(
            util.is_tuple_or_list("'string', 'of', 'stuff'"))

    def tests_validate_build_contents(self):
        content1 = {('set', '1')}
        content2 = [('set', '2')]
        content3 = [['set', '2']]
        util.validate_build_contents(content1, content2, content3)
