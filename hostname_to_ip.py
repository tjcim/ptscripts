#!/usr/bin/env python
"""
Get IP addresses associated with hostname

I use this when the client gives me URLs and I am doing an external pentest. I really want the IP
address instead of the URL, but I also want to make sure I get all IPs associated with the URL
in case they use multiple webservers.

Usage
-----
python hostname_to_ip.py -i "/path/to/file.txt" -o "/path/to/output.txt"

Parameters
----------
input : string
    Required - file with one url per line

output : string
    Optional - file to save the ips to

Output
------
"""
import logging
import argparse
from socket import gethostbyname
from urllib.parse import urlparse

from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.hostname_to_ip")


def get_ips(urls):
    ips = []
    for url in urls:
        LOG.info(f'Getting IP for URL: {url}')
        for _ in range(10):
            ip = gethostbyname(url)
            if ip not in ips:
                LOG.info(f'Adding IP: {ip}')
                ips.append(ip)
    return ips


def get_netloc(line):
    # Determine if it is a parsable format:
    parsed = urlparse(line)
    if parsed.scheme:
        # URL begins with http/https
        return parsed.netloc
    if "/" in line:
        # URL has a path, get everything before the "/"
        netloc = line.split("/")[0]
        return netloc
    # return the line as is
    return line


def main(args):
    LOG.info('Getting IPs against a text file of URLs.')
    urls = []
    ips = []
    with open(args.input, 'r') as f:
        for line in f:
            if line:
                LOG.info(f'Processing line: {line.strip()}')
                netloc = get_netloc(line.strip())
                urls.append(netloc)
    ips = get_ips(urls)
    with open(args.output, 'w') as f:
        f.write('\r\n'.join(ips))


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Hostnames to IPs.',
    )
    parser.add_argument('input', help='Path to input file: /root/pentests/blah/blah.txt')
    parser.add_argument('output', help='Path to place to save IPs: /root/pentests/blah/output.txt')

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
