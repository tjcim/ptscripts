"""
Run enum4linux save data and create images of the results

USAGE: python menum4linux.py <output_dir> --ip <ip>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.web_nikto")


def run_enum4linux(ip, output_dir, screenshot=False):
    html_path = os.path.join(output_dir, f"enum4linux_{ip}.html")
    command = f'enum4linux -a {ip}'
    LOG.info('Running command: ' + command)
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and screenshot:
        LOG.info("Creating a screenshot of the output and saving it to {}".format(screenshot))
        utils.dir_exists(screenshot, True)
        utils.selenium_image(html_output, screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def main(args):
    ips = []
    # Prepare commands
    if args.csv:
        LOG.info('Running enum4linux against CSV file.')
        ips_139 = utils.get_ips_with_port_open(args.csv, 139)
        if not ips_139:
            LOG.info('No computers with port 139 open.')
        ips_445 = utils.get_ips_with_port_open(args.csv, 445)
        if not ips_445:
            LOG.info('No computers with port 445 open.')
        ips = ips_139 + ips_445
    elif args.ip:
        LOG.info('Running enum4linux against a single IP.')
        ips.append(args.ip)
    else:
        LOG.info('Running enum4linux against a text file of IPs.')
        with open(args.txt, 'r') as f:
            for line in f:
                ips.append(line.strip())
    if args.screenshot:
        screenshot = args.screenshot
    else:
        screenshot = False
    for ip in ips:
        run_enum4linux(ip, args.output, screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run enum4linux against one or many targets.',
    )

    # Mutually exclusive inputs: csv, ip, list of ips.
    input_arg = parser.add_mutually_exclusive_group()
    input_arg.add_argument('--csv', help='CSV File of open ports.')
    input_arg.add_argument('--ip', help="Single url to be tested")
    input_arg.add_argument('--txt', help='Text file with ip per line.')

    parser.add_argument('output', help="where to store results")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshot will be saved.")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Logger set to debug.")
    else:
        logger.setLevel('INFO')

    if not args.csv and not args.ip and not args.txt:
        print('You must provide either a single ip (--ip), a CSV file (--csv) or a text file (--txt)')
        sys.exit()
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
