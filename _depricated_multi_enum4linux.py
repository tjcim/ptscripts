# Depricated by menum4linux
import os
import logging
import argparse
import subprocess

from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_enum4linux")


def create_command(ip, output_dir, proxy):
    if proxy:
        enum_command = 'proxychains enum4linux -a {}'.format(ip)
    else:
        enum_command = 'enum4linux -a {}'.format(ip)
    html_output = os.path.join(output_dir, "enum4linux_{ip}.html".format(ip=ip))
    return (enum_command, html_output)


def get_ips(csv_import):
    ips_139 = utils.get_ips_with_port_open(csv_import, 139)
    ips_445 = utils.get_ips_with_port_open(csv_import, 445)
    return ips_139 + ips_445


def run_enum4linux(enum_command):
    subprocess.call(enum_command.split())


def main(args):
    ips = get_ips(args.input)
    if not ips:
        LOG.info("No ips found with ports 139 or 445 open.")
        LOG.info("Exiting")
        raise SystemExit
    utils.dir_exists(args.output_dir, True)
    LOG.info("Saving output to {}".format(args.output_dir))
    for ip in ips:
        html_output, command = create_command(ip, args.output_dir, args.proxy)
        utils.run_command_tee_aha(command, html_output)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run enum4linux on multiple servers.',
        prog='multi_enum4linux.py',
    )
    parser.add_argument('input', help='CSV file')
    parser.add_argument('output_dir', help='Output directory where enum4linux reports will be created.')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
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
