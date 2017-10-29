import os
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_testssl")

# Unable to open a socket


def run_command_tee_aha(command, html_output):
    LOG.debug("Running command {}".format(command))
    try:
        process = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60 * 60 * 1)  # Give nikto an hour
        process_stdout = str(process.stdout, 'utf-8')
        p2 = subprocess.run(['tee', '/dev/tty'], input=process.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        LOG.warning("Timeout error occurred for url.")
        return
    if "Unable to open a socket" in process_stdout:
        LOG.info("The remote website didn't respons.")
        return
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    with open(html_output, 'wb') as h:
        h.write(output)


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


def main(args):
    testssl_folder = os.path.join(args.output, "testssl")
    utils.dir_exists(testssl_folder, True)
    for url in utils.parse_webserver_urls(args.input):
        if not utils.uses_encryption(url):
            LOG.debug("Skipping, no encryption: {}".format(url))
            continue
        if not utils.check_url(url):
            continue
        LOG.info("Testing url: {}".format(url))
        testssl_command, html_output = create_command(url, testssl_folder)
        LOG.debug("Saving output to {}".format(html_output))
        run_command_tee_aha(testssl_command, html_output)


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
