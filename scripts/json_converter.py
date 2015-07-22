#!/usr/bin/python3
"""Convert minimal json to human readable format"""
import json
import argparse

def main():
    """Main method"""
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='file to prettify')
    parser.add_argument('outfile', help='file to write to')

    args = parser.parse_args()

    filename = args.infile
    outfile = args.outfile

    print("Remember, this converter does not keep the order so if it is"
          "important, make sure to fix this script!")

    with open(filename, 'r') as fileh:
        text = json.load(fileh)

    pretty_text = json.dumps(text, indent=4, separators=(',', ': '))
    with open(outfile, 'w') as fileh:
        fileh.write(pretty_text)

if __name__ == '__main__':
    main()
