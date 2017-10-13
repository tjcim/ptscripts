""" Common methods for the scripts. """
import os
import csv
import time
import logging
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import config
from commands import COMMANDS
import logging_config  # noqa pylint: disable=unused-import


ASSESSMENT_TYPES = {
    "web": "Web Application Assessment",
    "pentest": "External Pentest",
}


module_log = logging.getLogger("ptscripts.utils")


def find_vulnerability(vulnerabilities, vuln_id):
    """ Searches the list of Vulnerability objects and returns the first with id == vuln_id else None """
    module_log.debug(vulnerabilities)
    for vuln in vulnerabilities:
        if vuln.id == vuln_id:
            return vuln
    return None


def print_commands(args, assessment_type):
    log = logging.getLogger("ptscripts.utils.print_commands")
    netloc = urlparse(args.url).netloc
    log.debug("netloc: " + netloc)
    folder_path = os.path.join(config.BASE_PATH, args.name)
    file_path = os.path.join(folder_path, "web_commands.txt")
    log.debug("file_path: " + file_path)
    log.info("Writing header information.")
    with open(file_path, 'w') as file_handler:
        header = "# {assessment_type} commands created for {pentest_name} on {time} using version {version}\r\n"
        header_text = header.format(
            assessment_type=ASSESSMENT_TYPES[assessment_type],
            pentest_name=args.name, time=time.asctime(), version=config.VERSION
        )
        file_handler.write(header_text)
        file_handler.write("#" + ("*" * len(header)) + "\r\n\r\n")
    for command_item in COMMANDS:
        if assessment_type not in command_item["tags"]:
            log.debug("{} not found in {}.".format(assessment_type, command_item["tags"]))
            continue
        log.info("Writing {} command".format(command_item["name"]))
        formatted_command = command_item["command"].format(
            url=args.url, output_dir=folder_path, netloc=netloc, scripts_dir=config.SCRIPTS_PATH)
        with open(file_path, 'a') as file_handler:
            try:
                log.debug("Writing comments: {}".format(command_item["comments"]))
                for comment in command_item["comments"]:
                    if comment:
                        file_handler.write("# {}\r\n".format(comment))
            except KeyError:
                # No comments
                pass
            log.debug("Writing command: {}".format(formatted_command))
            file_handler.write("{}\r\n\r\n".format(formatted_command))
    log.info("All commands written.")


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
