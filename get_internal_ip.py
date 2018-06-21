import sys
import telnetlib
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from bs4 import BeautifulSoup

from utils.utils import parse_csv_for_webservers


def run_get_internal_ip(webserver=None, url=None, port=None):
    if url:
        host = url
    else:
        host = webserver['ipv4']
    if port:
        port = port
    else:
        port = webserver['port']
    tn = telnetlib.Telnet(host, port)
    tn.write(b'GET /images\r\n')
    tn.write(b'exit\r\n')
    try:
        html_resp = tn.read_all()
    except Exception as e:  # pylint: disable=bare-except, broad-except
        print(e)
        sys.exit()
    soup = BeautifulSoup(html_resp, 'html.parser')
    redirect_tag = soup.find('a')
    try:
        href = redirect_tag.get('href')
        url_parts = urlparse(href)
        if not host == url_parts.netloc:
            print("Possible internal ip: {0}:{1}".format(host, url_parts.netloc))
        print(url_parts.netloc)
    except AttributeError as e:
        print(e)


def run_get_internal_ip_on_webservers(args):
    if args.input:
        webservers = parse_csv_for_webservers(args.csv_input)
        for webserver in webservers:
            run_get_internal_ip(webserver)
    else:
        run_get_internal_ip(url=args.url, port=args.port)


def parse_args():
    parser = argparse.ArgumentParser(prog='get_internal_ip.py')
    parser.add_argument('-i', '--input', help='CSV File with a list of urls to check)')
    parser.add_argument('-u', '--url', help='Url to check')
    parser.add_argument('-p', '--port', help='Port to check')
    return parser.parse_args()


if __name__ == '__main__':
    run_get_internal_ip_on_webservers(parse_args())
