import logging
import argparse

import utils
import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_enum4linux")


def main(args):
    LOG.info("Checking for ips with port {} open.".format(args.port))
    ips = utils.get_ips_with_port_open(args.input, args.port)
    for ip in ips:
        print("ip: {} has port {} open.".format(ip, args.port))


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Prints ips with port open',
        prog='port_open.py',
    )
    parser.add_argument('input', help='CSV file')
    parser.add_argument('port', help='Port')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
