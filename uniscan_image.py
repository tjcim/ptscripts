"""
Run uniscan save data and create images of the results

USAGE: python uniscan_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.uniscan_image")


def main(args):
    LOG.info("Running uniscan on {}".format(args.url))
    netloc = urlparse(args.url).netloc
    domain = netloc.split(":")[0]
    url = urlparse(args.url).scheme + "://" + netloc + urlparse(args.url).path
    command = "uniscan -u {url} -qweds".format(url=url)
    html_path = os.path.join(args.output, "uniscan_{}.html".format(domain))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        LOG.info("Creating a screenshot of the output and saving it to {}".format(args.screenshot))
        utils.dir_exists(args.screenshot, True)
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture uniscan data and image.',
    )
    parser.add_argument('url', help="url to be tested")
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
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
