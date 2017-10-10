import os
import argparse
import subprocess

import config
from utils import get_ips_with_port_open


def run_ike(ike_ips, wordlist=None):
    for ip in ike_ips:
        ikebrute_script = os.path.join(config.IKEBRUTE_PATH, 'ikebrute.sh')
        command_text = 'sh {} {}'.format(ikebrute_script, ip)
        if wordlist:
            command_text += " {}".format(wordlist)
        # command_text = 'ike-scan -M -A --id=sungardas {}'.format(ip)
        command = command_text.split()
        try:
            subprocess.call(command)
        except KeyboardInterrupt:
            return


def run_ike_on_ips(csv_input, wordlist):
    """ Select ips with open ports 500 and then run ike_scan """
    ike_ips = get_ips_with_port_open(csv_input, 500)
    run_ike(ike_ips, wordlist)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_ike.py')
    parser.add_argument('input', help='CSV File of open ports.')
    parser.add_argument(
        '--wordlist', default=None,
        help='Wordlist to use with psk-crack, if not provided we will use psk-crack-dictionary')
    return parser.parse_args()


if __name__ == '__main__':
    run_ike_on_ips(parse_args().input, parse_args().wordlist)
