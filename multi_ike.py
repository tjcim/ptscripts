import sys
import argparse
import subprocess

from utils import get_ips_with_port_open


def run_ike(ike_ips):
    for ip in ike_ips:
        command_text = 'ike-scan -M -A --id=test {}'.format(ip)
        command = command_text.split()
        try:
            subprocess.call(command)
        except KeyboardInterrupt:
            return


def run_ike_on_ips(args):
    """ Select ips with open ports 500 and then run ike_scan """
    ike_ips = get_ips_with_port_open(args.input, 500)
    run_ike(ike_ips)


def parse_args(args):
    parser = argparse.ArgumentParser(prog='multi_ike.py')
    parser.add_argument('input', help='CSV File of open ports.')
    return parser.parse_args(args)


if __name__ == '__main__':
    run_ike_on_ips(parse_args(sys.argv[1:]))
