#!/usr/bin/env python3
"""Correlation parser

Query correlation file with a package name and get recommended tests to run.
"""

from __future__ import print_function
import argparse
import json
import sys
import operator

MAX_NBR_OF_TESTS = 1203
NBR_OF_TESTS = 1203


def read_data(filename):
    """Read json data from filename"""
    data = {}
    try:
        with open(filename, 'r') as fileh:
            data = json.loads(fileh.read())
    except (OSError, IOError):
        pass
    return data


def get_tests(module, data):
    """Get tests correlated to module in dict data"""
    tests = {}
    try:
        tests = data[module]
    except KeyError:
        pass
    return tests


def parse_args():
    """setup argparser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='json file to analyze')
    parser.add_argument('module', help='module(s) to get recommendations on. '
                        'If many modules, separate their names by comma '
                        'without spaces, ie  "mod1,mod2,etc".')
    parser.add_argument('-c', '--cutoff', help='cutoff limit for correlation '
                        'weights', default=0, type=int)
    parser.add_argument('--history', type=int, default=6,
                        choices=[3, 6, 12, 24], help='time frame '
                        'from which to analyze.')
    parser.add_argument('--mode', default='narrow',
                        choices=['wide', 'narrow'], help='regression test '
                                                         'strategy.')
    parser.add_argument('--delimiter', help='delimiter for module list',
                        default=':')
    parser.add_argument('-v', '--verbose', action="store_true", help='prints '
                        'additional information')
    return parser.parse_args()


def narrow(args):
    filename = args.filename
    modules = args.module.split(args.delimiter)

    if args.verbose:
        print("\nParsing using narrow selection on file '{}' for recommendations on "
              "{}\n".format(filename, modules))

    data = read_data(filename)
    if not data:
        print("ERROR: File {} not found".format(filename))
        sys.exit(1)

    tests = {}
    empty_tests = []
    for module in modules:
        current_module_tests = get_tests(module, data)
        if not current_module_tests:
            empty_tests.append(module)
        tests = {k: tests.get(k, 0) + current_module_tests.get(k, 0) for k in
                set(tests) | set(current_module_tests)}

    if not tests:
        print("ERROR: Module of name {} not found in correlation "
              "data".format(module))
        sys.exit(1)

    ordered_tests = sorted(tests.items(), key=operator.itemgetter(1, 0))

    if args.verbose:
        print("Recommended tests:")
        for test in ordered_tests:
            if test[1] >= args.cutoff:
                print("{: <5} {}".format(test[1], test[0]))

        if args.cutoff:
            print("(cutoff at weight {})".format(args.cutoff))

        print("\nTotal recommended tests: {}".format(len(ordered_tests)))

        time_saved = MAX_NBR_OF_TESTS - len(ordered_tests)
        print("\nTime savings running only recommended tests: {} units "
              "".format(time_saved))

        if empty_tests:
            print("[INFO]: no tests found for {}".format(', '.join(empty_tests)))
    else:
        to_print = []
        for test in ordered_tests:
            if test[1] >= args.cutoff:
                to_print.append(test[0])

        print(','.join(to_print))


def wide(args):
    filename = args.filename

    if args.verbose:
        print("\nParsing using wide selection on file '{}'"
              "\n".format(filename))

    with open(filename, 'r') as fileh:
        string_data = fileh.read()

    data = json.loads(string_data)

    tests = sum_tests(data)
    sorted_tests = sorted(tests.items(), key=operator.itemgetter(1, 0))

    if args.verbose:
        for item in sorted_tests:
            print("{: >6} | {}".format(item[1], item[0]))

        print("weight | name")

        time_savings_percentage = (1 - len(sorted_tests) / NBR_OF_TESTS) * 100
        print("Nbr of correlated tests: {}".format(len(sorted_tests)))
        print("Time savings: {:.1f}%".format(time_savings_percentage))
    else:
        to_print = []
        for item in sorted_tests:
            to_print.append(item[0])

        print(','.join(to_print))


def sum_tests(data):
    """Go through each package in data, get the tests and their correlations,
    and add test and correlation to a list. If test already exists, increment
    weight by the weight of the test found."""
    tests = {}
    for package in data:
        for test in data[package]:
            if test in tests:
                tests[test] += data[package][test]
            else:
                tests[test] = data[package][test]

    return tests


def test_sum_tests():
    """Test sumt test func"""
    data = {'pak1': {'test1': 2, 'test2': 5},
            'pak2': {'test1': 1, 'test3': 7},
            'pak3': {'test1': 1, 'test3': 1}}

    tests = sum_tests(data)
    assert tests == {'test1': 4, 'test2': 5, 'test3': 8}


def main():
    """Main method"""

    args = parse_args()

    if args.mode == 'narrow':
        narrow(args)

    if args.mode == 'wide':
        wide(args)

if __name__ == "__main__":
    main()
