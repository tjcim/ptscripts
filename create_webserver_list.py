#!/usr/bin/env python
"""
Create a webserver file with a url per line.

This script takes a csv file (created by nmap_to_csv.py) and builds a list of all of the servers that are running websites. It saves the output to a file that can be used by other scripts.

Usage
-----
python create_webserver_list.py /full/path/to/ports.csv /full/path/to/pentest/folder/

Parameters
----------
input : string
    Required - Full path to ports.csv file (created by the nmap_to_csv.py script.)
output : string
    Required - Full path to the output directory. The script will save the file to <output>/webservers.txt

Output
------
webservers.txt - created within the directory specified in output.
"""
import os
import logging
import argparse

from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import

log = logging.getLogger("ptscripts.create_webserver_list")


def get_webserver_list(nmap_dict):
    webservers = []
    for host in nmap_dict:
        if host['service_name'] and host['service_name'] in ["http", "https"]:
            # scheme
            if host['service_tunnel'] == 'ssl':
                scheme = 'https'
            else:
                scheme = 'http'

            # if scheme is http and it is not on port 80, add port info.
            if scheme == 'http' and str(host['port']) != '80':
                port = ":" + str(host['port'])
            # if scheme is https and it is not on port 443, add port info.
            elif scheme == 'https' and str(host['port']) != '443':
                port = ":" + str(host["port"])
            # scheme is http and port is 80 or scheme is https and port is 443.
            else:
                port = ""

            formatted_url = scheme + "://" + host['ipv4'] + port + '/'
            log.debug("Adding url: {}".format(formatted_url))
            webservers.append(formatted_url)
    return webservers


def main(args):
    log.info("Starting to extract urls from {}".format(args.input))
    hosts = utils.csv_to_dict(args.input)
    webservers = get_webserver_list(hosts)
    output_file = os.path.join(args.output, "webservers.txt")
    log.info("Writing urls to {}".format(output_file))

    with open(output_file, 'w') as f:
        for webserver in webservers:
            f.write(webserver + '\r\n')


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Extract URLs from ports.csv to a file.',
    )
    parser.add_argument('input', help="full path to ports.csv file.")
    parser.add_argument('output', help="full path to where the 'webservers.txt' file will be saved.")
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
