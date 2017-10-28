#!/usr/bin/env python
"""
Parse nmap.xml to a csv file named ports.csv

Usage
-----
python nmap_to_csv.py /path/to/nmap.xml /path/to/output/dir/

Parameters
----------
input_file : string
    Required - full path to nmap.xml file
output_dir : string
    Required - full path to output directory

Output
------
Creates a file named ports.csv in the [output_dir] with only the open ports listed in the nmap.xml file.

columns:
    ip, port, service_name, tunnel, protocol
"""
import os
import csv
import sys
import logging
import argparse
import xml.etree.ElementTree as etree

from utils import logging_config  # noqa pylint: disable=unused-import

LOG = logging.getLogger("ptscripts.nmap_to_csv")


def get_all_hosts(root):
    """ Searches root for all hosts, returns list. """
    return root.findall('host')


def get_ipv4(host):
    """ Returns the ipv4 address of the host. """
    return host.find("./address/[@addrtype='ipv4']").get('addr')


def get_mac(host):
    """ Returns the mac address of the host. """
    try:
        mac = host.find("./address/[@addrtype='mac']").get('addr')
        return mac
    except AttributeError:
        LOG.debug("Couldn't get mac address for host.")
        return


def get_hostnames(host):
    """ Returns any hostnames collected. """
    hostname_list = []
    try:
        hostnames = host.findall("./hostnames/hostname")
        for hostname in hostnames:
            hostname_list.append(hostname.get('name'))
        return hostname_list
    except AttributeError:
        return


def get_all_ports(host):
    """ Return all ports from host. """
    try:
        return host.findall("./ports/port")
    except AttributeError:
        return


def is_open(port):
    """ Return boolean, True if port state='open'. """
    try:
        return port.find('state').get('state') == 'open'
    except AttributeError:
        return


def get_protocol(port):
    """ Return the protocol in use for port. """
    try:
        return port.get('protocol')
    except AttributeError:
        return


def get_port(port):
    """ Return the port in use. """
    try:
        return port.get('portid')
    except AttributeError:
        return


def get_service_name(port):
    """ Return the service name. """
    try:
        return port.find('service').get('name')
    except AttributeError:
        return


def get_service_tunnel(port):
    """ Return the service tunnel. """
    try:
        return port.find('service').get('tunnel')
    except AttributeError:
        return


def get_product(port):
    """ Return product information. """
    try:
        return port.find('service').get('product')
    except AttributeError:
        return


def get_version(port):
    """ Return version information. """
    try:
        return port.find('service').get('version')
    except AttributeError:
        return


def get_banner(port):
    """ Gets banner info if present. """
    try:
        return port.find('./script/[@id="banner"]').get('output')
    except AttributeError:
        return


def write_nmap_csv(output_file, hosts):
    """ Write the parsed hosts to the csv file. """
    header = [
        "port", "protocol", "ipv4", "mac", "hostnames", "service_name",
        "service_tunnel", "product_name", "product_version", "banner",
    ]
    with open(output_file, "w", newline='') as f:
        csvwriter = csv.writer(f)
        # Write header
        csvwriter.writerow(header)
        # Write results
        for host in hosts:
            for port in host["ports"]:
                csvwriter.writerow([
                    port["port"], port["protocol"], host["ipv4"], host["mac"],
                    " ".join(host["hostnames"]), port["service_name"], port["service_tunnel"],
                    port["product"], port["version"], port["banner"]
                ])


def parse_nmap(args):  # pylint: disable=too-many-locals
    output_file = os.path.join(args.output_dir, 'ports.csv')

    # Read in xml file
    tree = etree.parse(args.input_file)
    root = tree.getroot()

    hosts = []
    for host in get_all_hosts(root):
        host_info = {
            "ipv4": get_ipv4(host), "mac": get_mac(host), "hostnames": get_hostnames(host),
            "ports": [],
        }
        for port in get_all_ports(host):
            if not is_open(port):
                continue
            port_info = {
                "protocol": get_protocol(port), "port": get_port(port),
                "service_name": get_service_name(port), "service_tunnel": get_service_tunnel(port),
                "product": get_product(port), "version": get_version(port),
                "banner": get_banner(port),
            }
            host_info['ports'].append(port_info)
        hosts.append(host_info)
    write_nmap_csv(output_file, hosts)


def parse_args(args):
    parser = argparse.ArgumentParser(prog='nmap_to_csv.py')
    parser.add_argument('input_file', help='Nmap xml file to parse.')
    parser.add_argument('output_dir', help='Output directory to create.')
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    parse_nmap(parse_args(sys.argv[1:]))
