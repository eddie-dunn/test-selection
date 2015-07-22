#!/usr/bin/env python3
"""Main module for running the Difference Engine"""
#from diff.util import timeit
from util.util import json_dumps
from diff.difference_engine import parse_json
from diff.difference_engine import correlate
from diff.difference_engine import printable_analysis

# External imports
import argparse
import logging


#@timeit
def main():
    """Main method to run Difference Engine™ standalone"""
    default_cutoff = 0
    #default_outputfile = '/tmp/correlation.json'
    #default_diffdump = '/tmp/diffdump.json'

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="JSON file to analyze")
    parser.add_argument('output', help='Output file for correlation json data')
    parser.add_argument('-l', '--loglevel', help="Loglevel, valid values are: "
                        "DEBUG, INFO, WARNING, ERROR, CRITICAL",
                        default='WARNING')
    parser.add_argument('-c', '--cutoff',
                        help="Cutoff level for correlations. Defaults to "
                        "{}".format(default_cutoff),
                        type=int, default=default_cutoff)
    parser.add_argument('--print', action='store_true', dest='print_',
                        help='print output to stdout as well')
    parser.add_argument('--minimized', '-m', action='store_true',
                        help='store output as minimized json',)
    parser.add_argument('--diffdump',  '-d',
                        help='dump the difference data that the correlations '
                        'are calculated from as well.')
    args = parser.parse_args()

    diffdump = args.diffdump
    filename = args.filename
    output = args.output
    pretty = True if not args.minimized else False

    # Set loglevel
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)

    logformat = "[%(levelname)s: %(message)s]"
    logging.basicConfig(name='difference_engine', format=logformat,
                        level=args.loglevel)

    with open(filename, 'r') as fileh:
        text = fileh.read()

    print("analyzing and generating diff...")
    diff = parse_json(text)
    print("correlating diff...")
    correlation = correlate(diff)

    # Append json extension if not provided
    if not output.endswith(".json"):
        output = output + ".json"

    with open(output, 'w') as fileh:
        print("Writing {}correlation to {}.".format(
            "pretty " if pretty else "", output))
        fileh.write(json_dumps(correlation, pretty=pretty))

    if diffdump:  # Write diffdump if set
        with open(diffdump, 'w') as fileh:
            print("Writing diffdump to {}.".format(diffdump))
            fileh.write(json_dumps(diff, pretty=pretty))

    if args.print_:
        print('\n'.join(printable_analysis(correlation, cutoff=args.cutoff)))

if __name__ == "__main__":
    main()
