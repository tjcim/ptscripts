""" Common methods for the scripts. """
import os
import csv
import logging
import argparse
import subprocess
from io import BytesIO
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import urllib3
import requests
from PIL import Image
from selenium import webdriver  # pylint: disable=import-error

# from ptscripts import config
from utils import logging_config  # noqa pylint: disable=unused-import


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LOG = logging.getLogger("ptscripts.utils")


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
        if host.get('service_name') and host['service_name'] in ["http", "https"]:
            webservers.append(host)
    return webservers


def dir_exists(dir_path, make=True):
    """ Check that dir_path exists and is a directory
    if make is True it will try to make the dir"""
    if os.path.exists(dir_path):
        return os.path.isdir(dir_path)
    if make:
        LOG.info("Directory {} doesn't exist, going to try and create it.".format(dir_path))
        os.mkdir(dir_path)
        LOG.info("Directory created.")
        return True
    LOG.info("Directory {} doesn't exist and was not created.".format(dir_path))
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


def run_command_two(command, html_output, timeout=60 * 5):
    LOG.debug("Running command {}".format(command))
    p1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)  # pylint: disable=no-member
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    p1.stdout.close()
    p2.stdout.close()
    if timeout > 0:
        p1.wait(timeout=timeout)
    output = p3.communicate()[0]
    LOG.debug("Writing output to {}".format(html_output))
    command_text = "<p style='color:#00CC00'>{}</p>".format(command)
    with open(html_output, 'wb') as h:
        h.write(command_text.encode())
        h.write(output)
    LOG.info("HTML file written to {}".format(html_output))
    return html_output


def run_command_tee_aha(command, html_output, timeout=60 * 5):
    LOG.debug("Running command {}".format(command))
    try:
        p1 = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=timeout)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        LOG.warning("Timeout error occurred.")
        return
    p2 = subprocess.run(['tee', '/dev/tty'], input=p1.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    command_text = "<p style='color:#00CC00'>{}</p>".format(command)
    with open(html_output, 'wb') as h:
        h.write(command_text.encode())
        h.write(output)
    return html_output


def check_url(url, timeout=10):
    """ Uses python requests library first for speed and to get the response code. """
    LOG.info("Checking url: {}".format(url))
    try:
        resp = requests.get(url, timeout=timeout, verify=False)
    except requests.exceptions.ConnectTimeout:
        LOG.info("Requests timed out. Moving on.")
        return False
    except requests.exceptions.ReadTimeout:
        LOG.info("Requests timed out. Moving on.")
        return False
    except requests.exceptions.ConnectionError:
        LOG.info("Connection error. Moving on.")
        return False
    except requests.exceptions.InvalidSchema:
        LOG.info("Received invalid schema. Moving on.")
        return False

    if resp.status_code in [404, 408, 403]:
        LOG.info("Response status code {}, skipping.".format(resp.status_code))
        return False
    LOG.info("Response status code {}, its good to go.".format(resp.status_code))
    return True


def selenium_image(html_file, ss_path):
    """ Take picture of output.
    Opens html_file with selenium, saves the screenshot to the ss_path folder
    """
    driver = webdriver.PhantomJS()
    LOG.info("opening file {}".format(html_file))
    driver.get("file://" + html_file)
    driver.set_window_size(800, 600)
    filename = os.path.split(html_file)[1].rsplit(".", 1)[0] + ".png"
    screenshot_path = os.path.join(ss_path, filename)
    LOG.info("Saving image to {}".format(screenshot_path))
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    im = im.crop((0, 0, 800, 600))
    im.save(screenshot_path)
    driver.close()
