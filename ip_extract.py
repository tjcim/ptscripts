"""
Read in file and extrapolate the individual ips and save them to {output_dir}/_ips.txt

input_file should be a text file with one entry per line. An entry can be one of 4 formats:
    cidr - example: 192.168.1.0/24
    dashed - example: 192.168.1.1-4
    dashed - example: 192.168.1.1-192.168.1.4
    single - example: 192.168.1.1

Parameters
----------
input_file : string
    Required - Full path to a file with the ips.
output_dir : string
    Required - Full path to the directory in which the "_ips.txt" file will be saved.
"""
import os
import sys
import struct
import socket
import logging.config
import argparse

from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import

log = logging.getLogger("ptscripts.ip_extract")


def cidr_to_ip_list(in_cidr):
    """ Accept IPs in cidr format and returns a list of IPs """
    log.info("Extrapolating ips in cidr format: " + in_cidr)
    (ip, cidr) = in_cidr.split('/')
    cidr = int(cidr)
    host_bits = 32 - cidr
    i = struct.unpack('>I', socket.inet_aton(ip))[0]  # note the endianness
    start = ((i >> host_bits) << host_bits) + 1  # clear the host bits
    end = i | ((1 << host_bits) - 1)
    ips = []
    for i in range(start, end):
        ips.append(socket.inet_ntoa(struct.pack('>I', i)))
    return ips


def dashed_ips_to_list(in_dashed):
    """ Accept IPs in dashed format and return list of ips """
    ips = []
    split_by_dash = in_dashed.split('-')
    if len(split_by_dash[1].split('.')) > 1:
        log.info("{} is formatted like this: x.x.x.x-x.x.x.y".format(in_dashed))
        (start_octets, start_ip) = split_by_dash[0].rsplit('.', 1)
        (end_octets, end_ip) = split_by_dash[1].rsplit('.', 1)
        log.debug("Start octets: {}, start_ip {}; end_octets: {}, end_ip {}".format(start_octets, start_ip, end_octets, end_ip))
        # Check that the third octet of start and end are equal if not raise valueerror
        # for now.
        if not start_octets == end_octets:
            log.error("Can't process {}. This script is not smart enough to process this entry yet.".format(in_dashed))
            return

        log.info("Starting {}.{} and ending with {}.{}".format(
            start_octets, start_ip, end_octets, end_ip))
    else:
        log.info("{} is formatted like this: x.x.x.x-x".format(in_dashed))
        (start_octets, start_ip) = split_by_dash[0].rsplit('.', 1)
        end_ip = split_by_dash[1]

    start_ip = int(start_ip)
    end_ip = int(end_ip)
    start = start_octets + "." + str(start_ip)
    ips.append(start)
    while start_ip < end_ip:
        start_ip += 1
        ip = start_octets + "." + str(start_ip)
        ips.append(ip)
    return ips


def extract_ips(args):
    out_ips = []
    with open(args.input_file, 'r') as f:
        for line in f:
            if "-" in line:
                log.info("{} - dashed".format(line.strip()))
                try:
                    out_ips.extend(dashed_ips_to_list(line.strip()))
                except TypeError:
                    break
            elif "/" in line:
                log.info("{} - cidr".format(line.strip()))
                out_ips.extend(cidr_to_ip_list(line.strip()))
            else:
                log.info("{} - single ip".format(line.strip()))
                out_ips.append(line.strip())
    output_file_name = os.path.join(args.output_dir, '_ips.txt')
    with open(output_file_name, 'w') as f:
        f.write('\r\n'.join(out_ips))


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Extract IPs from IP notation in a file.',
    )
    parser.add_argument('input_file', help='a file with ips listed in cidr or dashed format')
    parser.add_argument('output_dir', help='directory to write ips.txt file')
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
    extract_ips(parse_args(sys.argv[1:]))
