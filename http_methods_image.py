"""
Run nmap with http-methods script save data and create images of the results

USAGE: python http_methods_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.http_methods_image")


def main(args):
    LOG.info("Running nmap with http-methods script for {}".format(args.url))
    parsed_url = urlparse(args.url)
    netloc = parsed_url.netloc
    # if non-standard port break it up.
    if ":" in netloc:
        domain = netloc.split(":")[0]
        port = netloc.split(":")[1]
    # otherwise port is based on scheme
    else:
        domain = netloc
        if parsed_url.scheme == 'http':
            port = '80'
        else:
            port = '443'
    if parsed_url.path:
        command = "nmap --script http-methods --script-args http-methods.url-path='{path}' -p {port} {domain}".format(
            path=parsed_url.path, port=port, domain=domain
        )
    else:
        command = "nmap --script http-methods -p {port} {domain}".format(port=port, domain=domain)
    LOG.info(f"Running command: {command}")
    html_path = os.path.join(args.output, "http_methods_{}.html".format(domain))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture http-methods data and image.',
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
