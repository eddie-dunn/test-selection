#!/usr/bin/python3
"""Go through correlation data and add correlations and weights for all
packages.

Use for context independent test selection.
"""
from __future__ import print_function
import argparse
import json
import operator

NBR_OF_TESTS = 1203

def parse_args():
    """setup argparser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='correlation data file')
    args = parser.parse_args()
    return args


def main():
    """Main function"""
    args = parse_args()
    filename = args.filename
    with open(filename, 'r') as fileh:
        string_data = fileh.read()

    data = json.loads(string_data)

    tests = sum_tests(data)
    sorted_tests = sorted(tests.items(), key=operator.itemgetter(1, 0))

    to_print = []
    for item in sorted_tests:
        #print("{: >6} | {}".format(item[1], item[0]))
        to_print.append(item[0])

    print(','.join(to_print))

    # print("weight | name")

    time_savings_percentage = (1 - len(sorted_tests)/NBR_OF_TESTS)*100
    # print("Nbr of correlated tests: {}".format(len(sorted_tests)))
    # print("Time savings: {:.1f}%".format(time_savings_percentage))


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


if __name__ == "__main__":
    main()
