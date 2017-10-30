"""
Initiate a nessus_scan

Parameters
----------
input_file : string
    Required - Full path to a file with the ips (one per line).
scan_name : string
    Required - The name to use when initiating the scan.
"""
import logging
import argparse

from nessrest import ness6rest  # pylint: disable=import-error

from config import config
from utils import utils, logging_config  # noqa pylint: disable=unused-import

log = logging.getLogger("ptscripts.nessus_scan")


def run_nessus_scan(args):
    log.info("Initiating nessus scan using the ips in {}".format(args.input_file))
    targets = []
    with open(args.input_file, 'r') as fp:
        for line in fp:
            line = line.strip(' \t\n\r')
            targets.append(line)
    nessus_targets = ','.join(targets)
    log.debug("Nessus will scan these ips: {}".format(nessus_targets))
    scan = ness6rest.Scanner(
        url=config.NESSUS_URL,
        api_akey=config.NESSUS_ACCESS_KEY,
        api_skey=config.NESSUS_SECRET_KEY,
        insecure=True)
    scan.scan_add(nessus_targets, template='basic', name=args.scan_name)
    res = scan.scan_run()
    log.info(res)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='nessus_scan.py',
        parents=[utils.parent_argparser()],
        description='Initiate a nessus scan.',
    )
    parser.add_argument('input_file', help='File with ip addresses (one per line).')
    parser.add_argument('scan_name', help='Nessus Scan Name.')
    args = parser.parse_args()
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    run_nessus_scan(parse_args())
