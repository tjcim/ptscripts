""" Common methods for the scripts. """
import os
import csv
import logging
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import urllib3
import requests
import logging_config  # noqa pylint: disable=unused-import


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
module_log = logging.getLogger("ptscripts.utils")


def sort_vulnerabilities(vulnerabilities):
    sort_order = {"H": 0, "M": 1, "L": 2}
    return sorted(vulnerabilities, key=lambda v: sort_order[v.risk_level])


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


def csv_to_dict(csv_file):
    """ Reads the csv file into a dictionary. """
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results


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
    hosts = csv_to_dict(csv_file)
    for host in hosts:
        if host['service_name'] and host['service_name'] in ["http", "https"]:
            webservers.append(host)
    return webservers


def dir_exists(dir_path, make=True):
    """ Check that dir_path exists and is a directory
    if make is True it will try to make the dir"""
    if os.path.exists(dir_path):
        return os.path.isdir(dir_path)
    else:
        if make:
            module_log.info("Directory {} doesn't exist, going to try and create it.".format(dir_path))
            os.mkdir(dir_path)
            module_log.info("Directory created.")
            return True
        else:
            module_log.info("Directory {} doesn't exist and was not created.".format(dir_path))
            return False


def get_hosts_with_port_open(csv_file, port):
    hosts = []
    ports_dict = csv_to_dict(csv_file)
    for row in ports_dict:
        if row['port'] == str(port):
            hosts.append(row)
    return hosts


def get_ips_with_port_open(csv_file, port):
    """ Returns list of ips with the specified port open """
    hosts = get_hosts_with_port_open(csv_file, port)
    ips = [host['ipv4'] for host in hosts]
    return ips


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


def run_command_tee_aha(command, html_output):
    module_log.debug("Running command {}".format(command))
    try:
        p1 = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60 * 5)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        module_log.warn("Timeout error occurred.")
        return
    p2 = subprocess.run(['tee', '/dev/tty'], input=p1.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    module_log.debug("Writing output to {}".format(html_output))
    with open(html_output, 'wb') as h:
        h.write(output)


def check_url(url, timeout=10):
    """ Uses python requests library first for speed and to get the response code. """
    module_log.info("Checking url: {}".format(url))
    try:
        resp = requests.get(url, timeout=timeout, verify=False)
    except requests.exceptions.ConnectTimeout:
        module_log.info("Requests timed out. Moving on.")
        return False
    except requests.exceptions.ReadTimeout:
        module_log.info("Requests timed out. Moving on.")
        return False
    except requests.exceptions.ConnectionError:
        module_log.info("Connection error. Moving on.")
        return False

    if resp.status_code in [404, 408]:
        module_log.info("Response status code {}, skipping.".format(resp.status_code))
        return False
    else:
        module_log.info("Response status code {}, its good to go.".format(resp.status_code))
        return True
