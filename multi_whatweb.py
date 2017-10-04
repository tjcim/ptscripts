import os
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from ptscripts.utils import parse_webserver_urls, dir_exists


def run_whatweb(url, output_dir):
    url_parsed = urlparse(url)
    if url_parsed.scheme == 'http':
        port = '80'
    else:
        port = '443'
    if url_parsed.port:
        port = str(url_parsed.port)
    results_file = os.path.join(
        output_dir, 'whatweb_{}_{}.html'.format(url_parsed.netloc, port))
    whatweb_command = 'whatweb -v -a 3 {}'.format(url)
    p1 = subprocess.Popen(whatweb_command.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    with open(results_file, 'wb') as h:
        h.write(output)


def run_whatweb_on_webservers(url_file, output_dir):
    dir_exists(output_dir, True)
    urls = parse_webserver_urls(url_file)
    for url in urls:
        run_whatweb(url, output_dir)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_whatweb.py')
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where whatweb reports will be created.')
    return parser.parse_args()


if __name__ == '__main__':
    run_whatweb_on_webservers(parse_args().input, parse_args().output)
