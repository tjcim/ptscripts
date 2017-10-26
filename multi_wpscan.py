import os
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import utils


LOG = logging.getLogger("ptscripts.multi_wpscan")


def run_command_tee_aha(command, html_output):
    LOG.debug("Running command {}".format(command))
    try:
        process = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60 * 5)  # pylint: disable=no-member
        p2 = subprocess.run(['tee', '/dev/tty'], input=process.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        LOG.warn("Timeout error occurred for url.")
        return
    if "The remote website is up, but" or "seems to be down. Maybe" in str(p2.stdout, 'utf-8'):
        LOG.info("No Wordpress found at URL.")
        return
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    with open(html_output, 'wb') as h:
        h.write(output)


def create_command(url, output_dir):
    command = "wpscan -u {} --random-agent --follow-redirection --disable-tls-checks".format(url)
    url_parsed = urlparse(url)
    if url_parsed.scheme == 'http':
        port = '80'
    else:
        port = '443'
    if url_parsed.port:
        port = str(url_parsed.port)
    html_output = os.path.join(
        output_dir, 'wpscan_{}_{}.html'.format(url_parsed.netloc, port))
    return (command, html_output)


def main(args):
    utils.dir_exists(args.output_dir, True)
    for url in utils.parse_webserver_urls(args.input):
        LOG.info("Checking URL: {}".format(url))
        command, html_output = create_command(url, args.output_dir)
        run_command_tee_aha(command, html_output)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run wpscan on multiple urls.',
        prog='multi_wpscan.py',
    )
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output_dir', help='Output directory where wpscan reports will be created.')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
