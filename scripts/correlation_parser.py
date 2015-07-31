#!/usr/bin/python3
"""Correlation parser

Query correlation file with a package name and get recommended tests to run.
"""
import argparse
import json
import sys
import operator

MAX_NBR_OF_TESTS = 1203

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


def main():
    """Main method"""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='json file to analyze')
    parser.add_argument('module', help='module(s) to get recommendations on. '
                        'If many modules, separate their names by comma '
                        'without spaces, ie  "mod1,mod2,etc".')
    parser.add_argument('-c', '--cutoff', help='cutoff limit for correlation '
                        'weights', default=0, type=int)
    args = parser.parse_args()
    filename = args.filename

    modules = args.module.split(',')

    print("\nParsing file '{}' for recommendations on "
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

    print("Recommended tests:")
    for test in ordered_tests:
        if test[1] >= args.cutoff:
            print("{: <5} {}".format(test[1], test[0]))
            #print("{weight:{fill}{width}} {test}".format(weight=test[1],
            #      test=test[0], fill=' ', width=4))

    if args.cutoff:
        print("(cutoff at weight {})".format(args.cutoff))

    print("\nTotal recommended tests: {}".format(len(ordered_tests)))

    time_saved = MAX_NBR_OF_TESTS - len(ordered_tests)
    print("\nTime savings running only recommended tests: {} units "
          "".format(time_saved))

    if empty_tests:
        print("[INFO]: no tests found for {}".format(', '.join(empty_tests)))

if __name__ == "__main__":
    main()
