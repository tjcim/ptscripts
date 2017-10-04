import telnetlib
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from bs4 import BeautifulSoup

from ptscripts.utils import parse_csv_for_webservers


def run_get_internal_ip(webserver):
    host = webserver['ip_addr']
    port = webserver['port']
    tn = telnetlib.Telnet(host, port)
    tn.write(b'GET /images\r\n')
    tn.write(b'exit\r\n')
    try:
        html_resp = tn.read_all()
    except:  # pylint: disable=bare-except
        return
    soup = BeautifulSoup(html_resp)
    redirect_tag = soup.find('a')
    try:
        href = redirect_tag.get('href')
        url_parts = urlparse(href)
        if not host == url_parts.netloc:
            print("Possible internal ip: {0}:{1}".format(host, url_parts.netloc))
    except AttributeError:
        return


def run_get_internal_ip_on_webservers(csv_input):
    webservers = parse_csv_for_webservers(csv_input)
    for webserver in webservers:
        run_get_internal_ip(webserver)


def parse_args():
    parser = argparse.ArgumentParser(prog='get_internal_ip.py')
    parser.add_argument('input', help='File with a list of urls to check)')
    return parser.parse_args()


if __name__ == '__main__':
    run_get_internal_ip_on_webservers(parse_args().input)
