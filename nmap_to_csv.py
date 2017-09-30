import os
import argparse
import xml.etree.ElementTree as etree


def parse_nmap(input_file, output_dir):  # pylint: disable=too-many-locals
    """ Given an nmap.xml input_file it will write a csv file that contains
    'ip, port, service_name, tunnel (if it has one), protocol'

    The file is written to <output_dir>/ports.csv, it will overwrite any
    existing file. """

    output_file = os.path.join(output_dir, 'ports.csv')

    # Read in xml file
    tree = etree.parse(input_file)
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


def parse_args():
    parser = argparse.ArgumentParser(prog='nmap_to_csv.py')
    parser.add_argument('input', help='Nmap xml file to parse.')
    parser.add_argument('output', help='Output directory to create.')
    return parser.parse_args()


if __name__ == '__main__':
    parse_nmap(parse_args().input, parse_args().output)
