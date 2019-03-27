"""
Run recon_ng save data and create images of the results

USAGE: python recon_ng.py <domain> <output> [-s <screenshot directory>]
"""
import os
import logging
import argparse

from utils import utils, logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.recon_ng")


def run_bing(args):
    rc_bing = os.path.join(args.ptfolder, "rc_files/recon_bing.rc")
    command = "recon-ng -r {}".format(rc_bing)
    LOG.info("Running the command: {}".format(command))
    file_name = "recon_bing.html"
    html_path = os.path.join(args.output, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def run_google(args):
    rc_google = os.path.join(args.ptfolder, "rc_files/recon_google.rc")
    command = "recon-ng -r {}".format(rc_google)
    LOG.info("Running the command: {}".format(command))
    file_name = "recon_google.html"
    html_path = os.path.join(args.output, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def run_brute(args):
    rc_brute = os.path.join(args.ptfolder, "rc_files/recon_brute.rc")
    command = "recon-ng -r {}".format(rc_brute)
    LOG.info("Running the command: {}".format(command))
    file_name = "recon_brute.html"
    html_path = os.path.join(args.output, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and args.screenshot:
        utils.selenium_image(html_output, args.screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def main(args):
    LOG.info("Running recon-ng")
    os.makedirs(args.output, exist_ok=True)
    run_bing(args)
    run_google(args)
    run_brute(args)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture theharvester data and image.',
    )
    parser.add_argument('ptfolder', help="Full path to pentest folder (e.g. /root/pentests/tjcim/ept).")
    parser.add_argument('output', help="Full path to output folder (e.g. /root/pentests/tjcim/ept/recon_ng)")
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
