"""
Run whois save data and create images of the results

USAGE: python whois_image.py <output_dir> <domain> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.whois_image")


def main(args):
    LOG.info("Running whois for {}".format(args.domain))
    command = "whois -H {domain}".format(domain=args.domain)
    html_path = os.path.join(args.output, "whois_{}.html".format(args.domain))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        LOG.info("Creating a screenshot of the output and saving it to {}".format(args.screenshot))
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture whois data and image.',
    )
    parser.add_argument('output', help="full path to where the results will be saved.")
    parser.add_argument('domain', help="Domain to capture.")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshots will be saved.")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Logger set to debug.")
    else:
        logger.setLevel('INFO')
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
