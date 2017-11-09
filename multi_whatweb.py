import os
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from utils import utils


def run_whatweb(command, html_output):
    p1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    with open(html_output, 'wb') as h:
        h.write(output)


def create_command(url, output):
    url_parsed = urlparse(url)
    if url_parsed.scheme == 'http':
        port = '80'
    else:
        port = '443'
    if url_parsed.port:
        port = str(url_parsed.port)
    html_output = os.path.join(
        output, 'whatweb_{}_{}.html'.format(url_parsed.netloc, port))
    whatweb_command = 'whatweb -v -a 3 {}'.format(url)
    return (whatweb_command, html_output)


def main(args):
    utils.dir_exists(args.output, True)
    for url in utils.parse_webserver_urls(args.input):
        if utils.check_url(url)[0]:
            command, html_output = create_command(url, args.output)
            run_whatweb(command, html_output)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run whatweb on multiple urls.',
        prog='multi_whatweb.py',
    )
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where whatweb reports will be created.')
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
