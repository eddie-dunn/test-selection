#!/usr/bin/python3
"""Script to calculate the average time saving by running only tests that are
recommended from the analysis taken from the difference_engine"""

import argparse
import json
import numpy
import sys

def parse_args():
    """setup argparser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='correlation data file')

    args = parser.parse_args()

    return args


def get_test_sizes(data):
    """Get the number of tests for each module in data dict"""
    test_sizes = []
    for module in data:
        test_sizes.append(len(data[module]))

    return test_sizes


def main():
    """Main function"""
    args = parse_args()
    filename = args.filename

    with open(filename, 'r') as fileh:
        data = json.loads(fileh.read())

    if not data:
        print("Cant calculate avg of empty data!")
        sys.exit(1)

    test_sizes = get_test_sizes(data)

    mean = numpy.mean(test_sizes)
    median = numpy.median(test_sizes)
    maximum = max(test_sizes)
    minimum = min(test_sizes)

    template = "{} nbr tests run: {}"
    print(template.format('mean', mean))
    print(template.format('median', median))
    print("max nbr tests run: {}".format(maximum))
    print("min nbr tests run: {}".format(minimum))

    max_time = 420 # minutes
    avg_test_time = 420/1200  # minutes/test

    max_test_time = round(maximum*avg_test_time)
    print("minimal time savings: ~{} minutes".format(max_time - max_test_time))
    print("maximum selected test time: ~{} minutes".format(max_test_time))
    print("ie {:.1f}% of total time".format(max_test_time*100/max_time))


"""
    cutoff = 3
    filtered_sizes = [item for item in test_sizes if item >= cutoff]
    mean = numpy.mean(filtered_sizes)
    median = numpy.median(filtered_sizes)
    maximum = max(filtered_sizes)
    minimum = min(filtered_sizes)

    template = "{} nbr tests run: {}"
    print("\n\n")
    print("Avg time saving, filtered data:")
    print(template.format('mean', mean))
    print(template.format('median', median))
    print("max nbr tests run: {}".format(maximum))
    print("min nbr tests run: {}".format(minimum))
"""

if __name__ == "__main__":
    main()
