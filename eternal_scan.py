"""
Run eternal scanner save data and create images of the results

USAGE: python eternal_scan.py <output_dir> --ip <ip>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.eternal_scan")


def run_escan(ips_file, output_dir, screenshot=False):
    html_path = os.path.join(output_dir, "eternal_scan.html")
    command = f'escan -ck {ips_file}'
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
    LOG.info('Running escan against a text file of IPs.')
    if args.screenshot:
        screenshot = args.screenshot
    else:
        screenshot = False
    run_escan(args.ips, args.output, screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run escan against one or many targets.',
    )

    parser.add_argument('ips', help="full path to list of ips.")

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

    if not utils.file_is_executable('/opt/eternal_scanner/escan'):
        logger.error('I can\'t find escan. Please download eternal scanner and save to /opt/eternal_scanner')
        logger.error('From /opt run: "git clone https://github.com/peterpt/eternal_scanner"')
        logger.error('Then CD to /usr/local/sbin and create two symlinks:')
        logger.error('ln -s /opt/eternal_scanner/escan ./')
        logger.error('ln -s /opt/eternal_scanner/elog ./')
        sys.exit()
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
