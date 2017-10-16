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
import sys
import argparse
import xml.etree.ElementTree as etree


def parse_nmap(args):  # pylint: disable=too-many-locals
    output_file = os.path.join(args.output_dir, 'ports.csv')

    # Read in xml file
    tree = etree.parse(args.input_file)
    root = tree.getroot()
    results = []
    for child in root.findall('host'):
        ip = child.find('address').attrib['addr']
        for ports in child.findall('ports'):
            for port in ports.findall('port'):
                if port.find('state').attrib['state'] == 'open':
                    protocol = port.attrib['protocol'] or None
                    service_name = port.find('service').attrib['name']
                    try:
                        tunnel = port.find('service').attrib['tunnel']
                    except KeyError:
                        tunnel = None
                    results.append({
                        'ip': ip,
                        'port': port.attrib['portid'],
                        'service_name': service_name,
                        'tunnel': tunnel,
                        'protocol': protocol,
                    })
    with open(output_file, 'w') as f:
        for res in results:
            f.write('{0},{1},{2},{3},{4}\r\n'.format(
                res['ip'],
                res['port'],
                res['service_name'],
                res['tunnel'],
                res['protocol']
            ))


def parse_args(args):
    parser = argparse.ArgumentParser(prog='nmap_to_csv.py')
    parser.add_argument('input_file', help='Nmap xml file to parse.')
    parser.add_argument('output_dir', help='Output directory to create.')
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    parse_nmap(parse_args(sys.argv[1:]))
