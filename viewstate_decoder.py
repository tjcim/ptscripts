import base64
import argparse


def main(args):
    decoded = base64.b64decode(args.input).decode('utf-8', 'ignore')
    print(decoded)


def parse_args(args):
    parser = argparse.ArgumentParser(prog='viewstate_decoder.py')
    parser.add_argument('input', help='Viewstate')
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
