import os
import argparse
import subprocess
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from utils import parse_webserver_urls, uses_encryption, dir_exists


def run_testssl(url, output_dir):
    if not uses_encryption(url):
        return
    print('Starting testssl for {}'.format(url))
    url_parsed = urlparse(url)
    port = '443'
    if url_parsed.port:
        port = str(url_parsed.port)
    results_html_file = os.path.join(
        output_dir, 'testssl_{}_{}.html'.format(url_parsed.netloc, port))
    results_csv_file = os.path.join(
        output_dir, 'testssl_{}_{}.csv'.format(url_parsed.netloc, port))
    testssl_command = 'testssl.sh --csvfile {} {}'.format(results_csv_file, url)
    print('The command: ' + testssl_command)
    p1 = subprocess.Popen(testssl_command.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    with open(results_html_file, 'wb') as h:
        h.write(output)


def run_testssl_on_webservers(url_file, output_dir):
    dir_exists(output_dir, True)
    urls = parse_webserver_urls(url_file)
    for url in urls:
        run_testssl(url, output_dir)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_testssl.py')
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where testssl reports will be created.')
    return parser.parse_args()


if __name__ == '__main__':
    run_testssl_on_webservers(parse_args().input, parse_args().output)
