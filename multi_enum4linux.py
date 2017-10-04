import argparse
import subprocess

from ptscripts.utils import get_ips_with_port_open


def run_enum4linux(ips, proxy):
    for ip in ips:
        if proxy:
            enum_command = 'proxychains enum4linux -a {}'.format(ip)
        else:
            enum_command = 'enum4linux -a {}'.format(ip)
        subprocess.call(enum_command.split())


def run_enum4linux_on_ips(csv_import, proxy):
    ips_139 = get_ips_with_port_open(csv_import, 139)
    ips_445 = get_ips_with_port_open(csv_import, 445)
    ips = ips_139 + ips_445
    run_enum4linux(ips, proxy)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_enum4linux.py')
    parser.add_argument('input', help='CSV file')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    run_enum4linux_on_ips(parse_args().input, parse_args().proxy)
