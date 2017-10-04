""" Common methods for the scripts. """
import os
import csv
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error


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
