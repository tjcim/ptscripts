"""
Run nslookup and create images of the results

USAGE: python nslookup_images.py <output_dir> <screenshot_dir> <domain>
"""
import re
import os
import logging
import argparse
import subprocess

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.nslookup_images")


def run_nslookup(domain, output_dir, record_type=None, nameserver=None):
    html_output = os.path.join(output_dir, "nslookup_{}_{}.html".format(domain, record_type))
    if record_type:
        _type = "-type={} ".format(record_type)
    else:
        _type = ""
    if nameserver:
        _ns = " {}".format(nameserver)
    else:
        _ns = ""
    command = "nslookup {_type}{domain}{_ns}".format(_type=_type, domain=domain, _ns=_ns)
    LOG.debug("Running command {}".format(command))
    try:
        p1 = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60 * 5)  # pylint: disable=no-member
        nslookup_stdout = str(p1.stdout, 'utf-8')
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        LOG.error("Timeout error occurred.")
        raise SystemExit
    p2 = subprocess.run(['tee', '/dev/tty'], input=p1.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    command_text = "<p style='color:#00CC00'>{}</p>".format(command)
    with open(html_output, 'wb') as h:
        h.write(command_text.encode())
        h.write(output)
    return nslookup_stdout, html_output


def parse_nslookup_ns(content):
    ns_re = re.compile('nameserver = (.*)\.')  # pylint: disable=anomalous-backslash-in-string
    results = ns_re.findall(content)
    return results


def main(args):
    # Run nslookup query for Name Servers
    LOG.info("Running nslookup with type NS")
    content, ns_html = run_nslookup(args.domain, args.output, "NS")
    auth_nameservers = parse_nslookup_ns(content)
    # Run nslookup query for MX records
    _, mx_html = run_nslookup(args.domain, args.output, "MX", auth_nameservers[0])
    # Run nslookup query for SRV records
    _, srv_html = run_nslookup(args.domain, args.output, "SRV", auth_nameservers[0])
    # Run nslookup query for any records
    _, any_html = run_nslookup(args.domain, args.output, "ANY", auth_nameservers[0])
    # Take picture of html file
    if args.screenshot:
        for html_file in [ns_html, mx_html, srv_html, any_html]:
            utils.selenium_image(html_file, args.screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture nslookup data and images',
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
    else:
        logger.setLevel('INFO')
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
