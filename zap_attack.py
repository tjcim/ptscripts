import time
import argparse

from zapv2 import ZAPv2

import ptscripts.config as config
from ptscripts.utils import parse_webserver_urls, dir_exists


def run_zap_attack(url, zap):
    print('ZAP Attacking {}'.format(url))
    zap.urlopen(url)
    time.sleep(2)

    # spider
    scanid = zap.spider.scan(url)
    time.sleep(2)
    while (int(zap.spider.status(scanid)) < 100):
        print('Spider progress {}%'.format(zap.spider.status(scanid)))
        time.sleep(2)
    print('Spider completed for url: {}'.format(url))
    time.sleep(5)

    # forced browse

    # scan
    print('Starting scan of {}'.format(url))
    scanid = zap.ascan.scan(url)
    while (int(zap.ascan.status(scanid)) < 100):
        print('Scan progress {}%'.format(zap.ascan.status(scanid)))
        time.sleep(5)
    print('Scan completed')


def run_zap_attack_on_webservers(url_file, output_dir):
    dir_exists(output_dir, True)

    zap = ZAPv2(apikey=config.ZAP_API, proxies=config.ZAP_PROXIES)  # pylint: disable=unexpected-keyword-arg
    # Create new session
    zap.core.new_session(output_dir)

    urls = parse_webserver_urls(url_file)
    for url in urls:
        run_zap_attack(url, zap)


def parse_args():
    parser = argparse.ArgumentParser(prog='zap_attack.py')
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where zap session will be created.')
    return parser.parse_args()


if __name__ == '__main__':
    run_zap_attack_on_webservers(parse_args().input, parse_args().output)
