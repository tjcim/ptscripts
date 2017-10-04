import argparse

from nessrest import ness6rest  # pylint: disable=import-error

import ptscripts.config as config


def run_nessus_scan(ips, scan_name):
    scan = ness6rest.Scanner(
        url=config.NESSUS_URL,
        api_akey=config.NESSUS_ACCESS_KEY,
        api_skey=config.NESSUS_SECRET_KEY,
        insecure=True)
    scan.scan_add(ips, template='basic', name=scan_name)
    res = scan.scan_run()
    print(res)


def run_nessus_scan_on_ips(ip_file_path, scan_name):
    targets = []
    with open(ip_file_path) as fp:
        for line in fp:
            line = line.strip(' \t\n\r')
            targets.append(line)
    nessus_targets = ','.join(targets)
    run_nessus_scan(nessus_targets, scan_name)


def parse_args():
    parser = argparse.ArgumentParser(prog='nessus_scan.py')
    parser.add_argument('input', help='File with ip addresses.')
    parser.add_argument('scan_name', help='Nessus Scan Name.')
    return parser.parse_args()


if __name__ == '__main__':
    run_nessus_scan_on_ips(parse_args().input, parse_args().scan_name)
