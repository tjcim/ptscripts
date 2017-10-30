"""
Run fierce save data and create images of the results

USAGE: python fierce_image.py <output_dir> <domain> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.fierce_image")


def main(args):
    LOG.info("Running fierce for {}".format(args.domain))
    command = "fierce -dns {} -threads 3".format(args.domain)
    LOG.info("Running the command: {}".format(command))
    file_name = "fierce_{}.html".format(args.domain)
    html_path = os.path.join(args.output, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    html_output = utils.run_command_two(command, html_path, timeout=60 * 5)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture fierce data and image.',
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
