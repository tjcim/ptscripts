"""
Run nikto save data and create images of the results

USAGE: python nikto_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.web_nikto")
NIKTO_COMMAND = "nikto -C all -host {domain} -port {port}{root}{ssl}"


def main(args):
    LOG.info("Running nikto for {}".format(args.url))
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
    if parsed_url.scheme == 'https':
        ssl = " -ssl"
    else:
        ssl = ""
    if parsed_url.path:
        root = " -root " + parsed_url.path
    else:
        root = ""
    command = NIKTO_COMMAND.format(domain=domain, port=port, root=root, ssl=ssl)
    netloc = urlparse(args.url).netloc
    domain = netloc.split(":")[0]
    html_path = os.path.join(args.output, "nikto_{}.html".format(domain))
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
        description='Capture dirb data and image.',
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
