import argparse
import logging

import vfp2py

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Tool for rewriting Foxpro code in Python')
    parser.add_argument("--logging", help="file to convert", action='store_true')
    parser.add_argument("infile", help="file to convert", type=str)
    parser.add_argument("outfile", help="file to output to", type=str)
    parser.add_argument("search", help="directories to search for included files", type=str, nargs='*')
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    if args.logging:
        logging.basicConfig(level=logging.DEBUG)
    vfp2py.SEARCH_PATH += args.search
    vfp2py.convert_file(args.infile, args.outfile)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
