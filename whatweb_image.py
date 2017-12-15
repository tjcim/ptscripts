"""
Run whatweb save data and create images of the results

USAGE: python whatweb_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.whatweb_image")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"


def main(args):
    LOG.info("Running whatweb for {}".format(args.url))
    command_string = 'whatweb -v -a 3 --user-agent {ua} {url}'.format(ua=USER_AGENT, url=args.url)
    command = 'whatweb -v -a 3 --user-agent'.split()
    command += [USER_AGENT, args.url]
    LOG.info(command_string)
    netloc = urlparse(args.url).netloc
    domain = netloc.split(":")[0]
    html_path = os.path.join(args.output, "whatweb_{}.html".format(domain))
    text_output = run_commands.bash_command(command, split=False)
    html_output = run_commands.create_html_file(text_output, command_string, html_path)
    if html_output and args.screenshot:
        LOG.info("Creating a screenshot of the output and saving it to {}".format(args.screenshot))
        utils.dir_exists(args.screenshot, True)
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture whatweb data and image.',
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
