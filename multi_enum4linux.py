import argparse
import subprocess

from utils import get_ips_with_port_open


def create_command(ip, proxy):
    if proxy:
        enum_command = 'proxychains enum4linux -a {}'.format(ip)
    else:
        enum_command = 'enum4linux -a {}'.format(ip)
    return enum_command


def get_ips(csv_import):
    ips_139 = get_ips_with_port_open(csv_import, 139)
    ips_445 = get_ips_with_port_open(csv_import, 445)
    return ips_139 + ips_445


def run_enum4linux(enum_command):
    subprocess.call(enum_command.split())


def run_enum4linux_on_ips(csv_import, proxy):
    for ip in get_ips(csv_import):
        command = create_command(ip, proxy)
        run_enum4linux(command)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_enum4linux.py')
    parser.add_argument('input', help='CSV file')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    run_enum4linux_on_ips(parse_args().input, parse_args().proxy)
