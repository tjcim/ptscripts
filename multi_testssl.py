import os
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import utils
import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_testssl")


def create_command(url, output_dir):
    if not utils.uses_encryption(url):
        return
    url_parsed = urlparse(url)
    port = '443'
    if url_parsed.port:
        port = str(url_parsed.port)
    html_output = os.path.join(
        output_dir, 'testssl_{}_{}.html'.format(url_parsed.netloc, port))
    csv_output = os.path.join(
        output_dir, 'testssl_{}_{}.csv'.format(url_parsed.netloc, port))
    testssl_command = 'testssl.sh --csvfile {} {}'.format(csv_output, url)
    return testssl_command, html_output


def run_testssl(command, html_output):
    LOG.debug("Running command: {}".format(command))
    p1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    with open(html_output, 'wb') as h:
        h.write(output)


def main(args):
    utils.dir_exists(args.output, True)
    for url in utils.parse_webserver_urls(args.input):
        if not utils.uses_encryption(url):
            LOG.debug("Skipping, no encryption: {}".format(url))
            continue
        LOG.info("Testing url: {}".format(url))
        testssl_command, html_output = create_command(url, args.output)
        LOG.debug("Saving output to {}".format(html_output))
        run_testssl(testssl_command, html_output)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run testssl on multiple urls.',
        prog='multi_testssl.py',
    )
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where testssl reports will be created.')
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
