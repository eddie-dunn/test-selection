#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Main module for running the Difference Engine"""
# External imports
import argparse
import codecs
import logging

from diff.difference_engine import correlate
from diff.difference_engine import parse_json
from diff.difference_engine import printable_analysis
from util.util import json_dumps

NAME = __name__ if __name__ != '__main__' else "diffeng"
DEBUG_CHOICES = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def setup_logging(loglevel, logfile):
    """Setup logging."""
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    logformat = "[{}][%(asctime)s %(levelname)s] %(message)s".format(NAME)
    dateformat = "%H:%M:%S"
    if logfile:
        logging.basicConfig(filename=logfile, format=logformat,
                            level=loglevel, datefmt=dateformat)
    else:
        logging.basicConfig(format=logformat, level=loglevel,
                            datefmt=dateformat)



def main():
    """Main method to run Difference Engine™ standalone"""
    default_cutoff = 0
    # default_outputfile = '/tmp/correlation.json'
    # default_diffdump = '/tmp/diffdump.json'

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', help="JSON file to analyze")
    parser.add_argument('output', help='Output file for correlation json data')
    parser.add_argument('-l', '--loglevel', help="Set a loglevel",
                        choices=DEBUG_CHOICES,
                        default='WARNING')
    parser.add_argument('--logfile', default=None,
                        help="Log to file instead of stdout.")
    parser.add_argument('-c', '--cutoff',
                        help="Cutoff level for correlations.",
                        type=int, default=default_cutoff)
    parser.add_argument('--print', action='store_true', dest='print_',
                        help='print output to stdout as well')
    parser.add_argument('--minimized', '-m', action='store_true',
                        help='store output as minimized json',)
    parser.add_argument('--diffdump', '-d', default=None,
                        help='dump the difference data that the correlations '
                        'are calculated from as well.')
    args = parser.parse_args()

    # Deal with args
    diffdump = args.diffdump
    filename = args.filename
    output = args.output
    pretty = True if not args.minimized else False

    # Setup logging
    setup_logging(args.loglevel, args.logfile)

    logging.debug("Reading %s", filename)
    with codecs.open(filename, 'r', encoding="utf-8") as fileh:
        text = fileh.read()

    logging.debug("Parsing json...")
    diff = parse_json(text)

    logging.debug("Correlating...")
    correlation = correlate(diff)

    with codecs.open(output, 'w', encoding='utf-8') as fileh:
        logging.info("Writing %scorrelation to %s.",
                     "pretty " if pretty else "", output)
        fileh.write(json_dumps(correlation, pretty=pretty))

    if diffdump:  # Write diffdump if set
        with codecs.open(diffdump, 'w', encoding='utf-8') as fileh:
            logging.info("Writing diffdump to %s.", diffdump)
            fileh.write(json_dumps(diff, pretty=pretty))

    if args.print_:
        print('\n'.join(printable_analysis(correlation, cutoff=args.cutoff)))


if __name__ == "__main__":
    main()
