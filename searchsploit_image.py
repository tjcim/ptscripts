"""
Run searchsploit save data and create images of the results

USAGE: python searchsploit_image.py <input> <output> [-s <screenshot directory>]
searchsploit --nmap nmap.xml
"""
import os
import logging
import argparse
import subprocess

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.searchsploit_image")


def update_searchsploit():
    LOG.info("Running updating searchsploit")
    command = "searchsploit -u"
    try:
        subprocess.run(command.split(), timeout=60 * 5)  # timeout for 5 minutes
    except subprocess.TimeoutExpired:
        LOG.warning("Error updating searchsploit timeout error occurred.")
        return
    LOG.info("Searchsploit updated successfully.")


def get_search_terms(csv_file):
    terms = []
    ports = utils.csv_to_dict(csv_file)
    for port in ports:
        if port['product_name'] and port['product_name'] not in terms:
            terms.append(port['product_name'])
            LOG.debug("Adding term {}".format(port['product_name']))
    return terms


def run_searchsploit(command):
    LOG.debug("Running search: {}".format(command))
    try:
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60)
        subprocess.run(['tee', '/dev/tty'], input=proc.stdout)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:
        LOG.warning("Error updating searchsploit timeout error occurred.")
        return
    return proc.stdout


def run_aha(html_output, stdout):
    b_stdout = stdout.encode()
    try:
        p3 = subprocess.run(['aha', '-b'], input=b_stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:
        LOG.warning("Error running aha timeout error occurred.")
        return
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    with open(html_output, 'wb') as h:
        h.write(output)
    LOG.info("HTML file written to {}".format(html_output))
    return True


def main(args):
    if not args.no_update:
        update_searchsploit()
    search_terms = get_search_terms(args.input)
    stdout = ""
    for term in search_terms:
        command = "searchsploit {term}".format(term=term)
        stdout += "\rsearchsploit '{}'\r".format(term) + run_searchsploit(command).decode('utf-8')
    html_path = os.path.join(args.output, "searchsploit.html")
    LOG.info("Saving output to: {}".format(html_path))
    aha = run_aha(html_path, stdout)
    if aha and args.screenshot:
        utils.selenium_image(html_path, args.screenshot)
    if not html_path:
        LOG.error("Didn't receive a response from running aha.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture searchsploit data and image.',
    )
    parser.add_argument('input', help="full path to ports.csv file.")
    parser.add_argument('output', help="full path to where the results will be saved.")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshot will be saved.")
    parser.add_argument('-n', '--no-update', action='store_true',
                        help="If set searchsploit will not be updated.")
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
