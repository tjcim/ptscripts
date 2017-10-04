import argparse
import subprocess

from ptscripts.utils import parse_webserver_urls


def run_wpscan(webservers):
    for webserver in webservers:
        command_text = "wpscan -u {} --random-agent \
--follow-redirection --disable-tls-checks".format(webserver)
        command = command_text.split()
        try:
            subprocess.call(command)
        except KeyboardInterrupt:
            return


def run_wpscan_on_webservers(url_file):
    webservers = parse_webserver_urls(url_file)
    run_wpscan(webservers)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_wpscan.py')
    parser.add_argument('input', help='File with a URL each line.')
    return parser.parse_args()


if __name__ == '__main__':
    run_wpscan_on_webservers(parse_args().input)
