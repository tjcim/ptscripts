""" Common methods for the scripts. """
import os
import csv
import logging
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import logging_config  # noqa pylint: disable=unused-import


module_log = logging.getLogger("ptscripts.utils")


def sort_vulnerabilities(vulnerabilities):
    high = []
    medium = []
    low = []
    module_log.debug("Sorting vulnerabilities.")
    for vuln in vulnerabilities:
        module_log.debug("{} vuln risk {}".format(vuln.id, vuln.risk_level))
        if vuln.risk_level == 'H':
            module_log.debug("Adding {} to high".format(vuln.id))
            high.append(vuln)
        elif vuln.risk_level == 'M':
            module_log.debug("Adding {} to medium".format(vuln.id))
            medium.append(vuln)
        else:
            module_log.debug("Adding {} to low".format(vuln.id))
            low.append(vuln)
    sorted_vulns = []
    for vuln in high:
        sorted_vulns.append(vuln)
    for vuln in medium:
        sorted_vulns.append(vuln)
    for vuln in low:
        sorted_vulns.append(vuln)
    return sorted_vulns


def find_vulnerability(vulnerabilities, vuln_id):
    """ Searches the list of Vulnerability objects and returns the first with id == vuln_id else None """
    for vuln in vulnerabilities:
        if vuln.id == vuln_id:
            return vuln
    return None


def parent_argparser():
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--verbose', '-v', action='store_true', required=False,
                       help="Log debug to screen.")
    group.add_argument('--quiet', '-q', action='store_true', required=False,
                       help='Script will only output errors.')
    return parser


def uses_encryption(url):
    url_parsed = urlparse(url)
    return url_parsed.scheme == 'https'


def parse_webserver_urls(url_file):
    """ Reads in a file and returns a list of each line. """
    webserver_urls = []
    with open(url_file) as fp:
        for line in fp:
            line = line.strip(' \t\n\r')
            webserver_urls.append(line)
    return webserver_urls


def parse_csv_for_webservers(csv_file):
    webservers = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        host_ports = list(reader)
        for row in host_ports:
            if row[2] and (row[2] == 'http' or row[2] == 'https'):
                webservers.append({
                    'ip_addr': row[0],
                    'port': row[1],
                    'service_name': row[2],
                    'tunnel': row[3],
                })
    return webservers


def file_exists(file_path):
    """ Check that file_path exists and is a file returns True else False """
    if os.path.exists(file_path):
        return bool(os.path.isfile(file_path))
    else:
        return False


def dir_exists(dir_path, make=True):
    """ Check that dir_path exists and is a directory
    if make is True it will try to make the dir"""
    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            return True
        else:
            if make:
                os.mkdir(dir_path)
                return True
            return False
    else:
        if make:
            print("    Directory {} doesn't exist, going to try and create it.".format(dir_path))
            os.mkdir(dir_path)
            print("    Directory created.")
            return True
        else:
            print("    Directory {} doesn't exist and was not created.")
            return False


def get_ips_with_port_open(csv_file, port):
    """ Returns list of ips with the specified port open """
    # open csv_file and yield row
    # compare port to column and add to list if it matches
    # return list
    ip_list = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        host_ports = list(reader)
        for row in host_ports:
            if row[1] == str(port):
                ip_list.append(row[0])
    return ip_list


def csv_to_list(csv_file):
    """ Read csv file and return rows and columns in a list. """
    results = []
    with open(csv_file, 'r') as a_csv:
        a_csvreader = csv.reader(a_csv)
        for row in a_csvreader:
            results.append(row)
    return results


def write_list_to_csv(in_list, out_file):
    """ Write python list to csv file. """
    with open(out_file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(in_list)


def text_file_lines_to_list(in_file):
    """ Read a text file and return a list of each line item (minus the returns, spaces, etc.)"""
    lines = []
    with open(in_file) as fp:
        for line in fp:
            line = line.strip(' \t\n\r')
            lines.append(line)
    return lines


def find_files(input_dir, suffix='.csv'):
    filenames = os.listdir(input_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]
