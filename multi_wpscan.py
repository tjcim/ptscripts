import os
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import utils


def run_wpscan(command, html_output):
    p1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
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
        command, html_output = create_command(url, args.output_dir)
        run_wpscan(command, html_output)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run wpscan on multiple urls.',
        prog='multi_wpscan.py',
    )
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where wpscan reports will be created.')
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
