"""
Run yasuo save data and create images of the results

USAGE: python yasuo_image.py <output_dir> <input_file> [-s <screenshot directory>]
yasuo.rb -s /opt/yasuo/signatures.yaml -f /root/pentests/yardi/nmap.xml -t 10
"""
import os
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.yasuo_image")


def main(args):
    LOG.info("Running yasuo")
    command = "yasuo.rb -s /opt/yasuo/signatures.yaml -f {nmap_xml} -t 10".format(
        nmap_xml=args.input)
    LOG.info("Running the command: {}".format(command))
    html_path = os.path.join(args.output, "yasuo.html")
    LOG.info("Saving output to: {}".format(html_path))
    html_output = utils.run_command_two(command, html_path, timeout=60 * 60 * 5)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture yasuo data and image.',
    )
    parser.add_argument('input', help="full path to nmap xml file.")
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
