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
import sys
import logging
import argparse

import utils
import logging_config  # noqa pylint: disable=unused-import

log = logging.getLogger("ptscripts.create_webserver_list")


def get_webserver_list(nmap_list):
    webservers = []
    for host_port in nmap_list:
        if host_port[2] and "http" in host_port[2]:
            port = ""
            if host_port[3] == 'ssl':
                scheme = 'https'
            else:
                scheme = 'http'
            if not host_port[1] == "80":
                port = ":" + host_port[1]
            # if https and port 443 don't add the port info
            if (host_port[1] == '443') and (scheme == 'https'):
                port = ''
            formatted_url = scheme + "://" + host_port[0] + port + '/'
            log.debug("Adding url: {}".format(formatted_url))
            webservers.append(formatted_url)
    return webservers


def build_webservers_file(args):
    log.info("Starting to extract urls from {}".format(args.input))
    host_ports = utils.csv_to_list(args.input)
    webservers = get_webserver_list(host_ports)
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
    parser.add_argument('input')
    parser.add_argument('output')
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
    build_webservers_file(parse_args(sys.argv[1:]))
