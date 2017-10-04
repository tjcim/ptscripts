import argparse
import urllib3

import requests

import ptscripts.config as config
from ptscripts.utils import parse_webserver_urls


def run_burp(url):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print('Requesting url: {}'.format(url))
    requests.head(url, proxies=config.BURP_PROXIES, timeout=5, allow_redirects=False, verify=False)


def run_burp_on_webservers(url_file):
    urls = parse_webserver_urls(url_file)
    for url in urls:
        run_burp(url)


def parse_args():
    parser = argparse.ArgumentParser(prog='burp_requests.py')
    parser.add_argument('input', help='File with a URL each line.')
    return parser.parse_args()


if __name__ == '__main__':
    run_burp_on_webservers(parse_args().input)
