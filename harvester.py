"""
Run theharvester save data and create images of the results

USAGE: python harvester.py <output_dir> <domain> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils, logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.harvester")


def main(args):
    LOG.info("Running theharvester")
    os.makedirs(args.output, exist_ok=True)
    output = os.path.join(args.output, "harvester.html")
    command = """theharvester -d {domain} -b all -l 100 -f {output}""".format(
        domain=args.domain, output=output)
    LOG.info("Running the command: {}".format(command))
    file_name = "harvester_output.html"
    html_path = os.path.join(args.output, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture theharvester data and image.',
    )
    parser.add_argument('domain', help="Domain to be tested.")
    parser.add_argument('output', help="full path to where the results will be saved.")
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
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
