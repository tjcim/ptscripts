"""
Run onesixtyone save data and create images of the results

USAGE: python monesixtyone.py <output_dir> --ip <ip>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.monesixtyone")
COMMAND = "onesixtyone -c /usr/share/doc/onesixtyone/dict.txt -d -o {text_path} {ip}"


def run_onesixtyone(ip, output_dir, screenshot=False):
    html_path = os.path.join(output_dir, f"onesixtyone_{ip}.html")
    text_path = os.path.join(output_dir, f"onesixtyone_{ip}.txt")
    command = COMMAND.format(text_path=text_path, ip=ip)
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
        LOG.info('Running onesixtyone against CSV file.')
        ips = utils.get_ips_with_port_open(args.csv, 161)
    elif args.ip:
        LOG.info('Running onesixtyone against a single IP.')
        ips.append(args.ip)
    else:
        LOG.info('Running onesixtyone against a text file of URLs.')
        with open(args.txt, 'r') as f:
            for line in f:
                ips.append(line.strip())
    if args.screenshot:
        screenshot = args.screenshot
    else:
        screenshot = False
    for ip in ips:
        run_onesixtyone(ip, args.output, screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run onesixtyone against one or many targets.',
    )

    # Mutually exclusive inputs: csv, url, list of sites.
    input_arg = parser.add_mutually_exclusive_group()
    input_arg.add_argument('--csv', help='CSV File of open ports.')
    input_arg.add_argument('--ip', help="Single ip to be tested")
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
        print('You must provide either a single IP (--ip), a CSV file (--csv) or a text file (--txt)')
        sys.exit()
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
