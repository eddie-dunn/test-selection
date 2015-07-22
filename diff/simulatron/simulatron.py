#!/usr/bin/env python3
"""Main module for running Simulatron2"""

import util.util as util
import diff.simulatron.sim2 as sim2

import argparse

# Default values for test output
TESTNOISE = 0
PKGNOISE = 0
AVAILABLE_PACKAGES = 10
BUILDS_PER_PRODUCT = 3
PRODUCTS = 1


def main():
    """Main method"""
    args = parse_args()
    stdout = args.stdout
    filename = args.filename
    pretty = args.pretty

    superset = sim2.create_superset(args.products, args.packages, args.builds,
                                    args.pkgnoise, args.testnoise)

    if stdout:
        print(util.json_dumps(superset, pretty=pretty))

    if filename:
        with open(filename, 'w') as fileh:
            fileh.write(util.json_dumps(superset, pretty=pretty))


def parse_args():
    """Parse command line options"""
    default_outfile ='/tmp/simdata.json'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--filename',
        default=default_outfile,
        help='If output to file is set, this is the destination. Defaults to '
             '{}'.format(default_outfile))
    parser.add_argument(
        '-o',
        '--stdout',
        action='store_true',
        help="output to stdout")
    parser.add_argument(
        '-p',
        '--pretty',
        dest='pretty',
        action='store_true',
        help="If set, json output will be prettified. Defaults to False")

    # arguments to vary the output of the Simulatron
    parser.add_argument(
        '--testnoise',
        default=TESTNOISE,
        type=int,
        metavar='int',
        help="Amount of test noise to add to builds")
    parser.add_argument(
        '--pkgnoise',
        default=PKGNOISE,
        type=int,
        metavar='int',
        help="Amount of changed package noise to add to builds")
    parser.add_argument(
        '--builds',
        default=BUILDS_PER_PRODUCT,
        type=int,
        metavar='int',
        help="Amount of builds per product")
    parser.add_argument(
        '--packages',
        default=AVAILABLE_PACKAGES,
        type=int,
        metavar='int',
        help="Amount packages per build")
    parser.add_argument(
        '--products',
        default=PRODUCTS,
        type=int,
        metavar='int',
        help="Amount of products per simulation")

    args = parser.parse_args()
    if not (args.filename or args.stdout):
        args.stdout = True

    return args


if __name__ == '__main__':
    #ARGS = parse_args()
    main()
