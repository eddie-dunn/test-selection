#!/usr/bin/env python3
"""Correlation parser

Query correlation file with a package name and get recommended tests to run.

Written for Python3 but should support Python2 as well.
"""

from collections import defaultdict
import argparse
import json
import sys
import operator


MAX_NBR_OF_TESTS = 1203
MODE_CHOICES = ['WIDE', 'wide', 'NARROW', 'narrow']


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
    """Setup argparser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('modules', nargs='+', help='module(s) to get '
                        'recommendations on. Space separated list of modules. '
                        'Ignored if wide mode is specified.')
    parser.add_argument('-f', '--correlation-data', required=True,
                        help='json file to analyze')
    parser.add_argument('-c', '--cutoff', help='cutoff limit for correlation '
                        'weights', default=0, type=int)
    parser.add_argument('--mode', default='NARROW',
                        choices=MODE_CHOICES, help='regression test strategy.')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='prints additional information')
    parser.add_argument(
        '--sort', default='weight',
        help="Option to sort output in different ways",
        choices=['weight', 'weight-reverse', 'alphabet', 'alphabet-reverse'],
        dest='order',
    )
    return parser.parse_args()


def sort_tests(tests: dict, order: str) -> list:
    """Takes a dict containing str/int key/value pairs like:
        {'testsname': correlation_weight}

    Returns a list ordered as specified by parameter `order`.
    """
    if order == 'weight':
        return sorted(tests.items(), key=operator.itemgetter(1, 0))
    elif order == 'weight-reverse':
        return sorted(tests.items(), key=operator.itemgetter(1, 0))[::-1]
    elif order == 'alphabet':
        return sorted(tests.items())
    elif order == 'alphabet-reverse':
        return sorted(tests.items())[::-1]

    raise ValueError("Order '%s' is not supported" % order)


def narrow(filename, args):
    """Perform narrow test selection."""
    # TODO: Refactor this
    modules = args.modules

    if args.verbose:
        print("\nParsing using narrow selection on file '{}' for "
              "recommendations on {}\n".format(filename, modules))

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
        print("WARNING: No tests correlated to specified module(s):"
              "{}".format(modules))
        sys.exit(1)

    ordered_tests = sort_tests(tests, args.order)

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
        print_list([item[0] for item in ordered_tests])


def wide(filename, args):
    """Perform wide test selection."""
    # TODO: Refactor this
    if args.verbose:
        print("\nParsing using wide selection on file '{}'"
              "\n".format(filename))

    with open(filename, 'r') as fileh:
        string_data = fileh.read()

    data = json.loads(string_data)

    tests = sum_tests(data)
    sorted_tests = sort_tests(tests, args.order)

    if args.verbose:
        for item in sorted_tests:
            print("{: >6} | {}".format(item[1], item[0]))

        print("weight | name")

        time_savings_percentage = ((1 - len(sorted_tests) / MAX_NBR_OF_TESTS)
                                   * 100)
        print("Nbr of correlated tests: {}".format(len(sorted_tests)))
        print("Time savings: {:.1f}%".format(time_savings_percentage))
    else:
        print_list([item[0] for item in sorted_tests])


def print_list(test_list, sep='\n'):
    """Print a list of test items, newline separated by default."""
    print(sep.join(test_list))


def sum_tests(data):
    """Go through each package in data, get the tests and their correlations,
    and add test and correlation to a list. If test already exists, increment
    weight by the weight of the test found."""
    tests = defaultdict(int)
    for package in data:
        for test in data[package]:
            tests[test] += data[package][test]

    return tests


def main():
    """Main method"""

    args = parse_args()
    filename = args.correlation_data

    if args.mode.lower() == 'narrow':
        narrow(filename, args)

    if args.mode.lower() == 'wide':
        wide(filename, args)


if __name__ == "__main__":
    main()
