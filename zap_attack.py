import time
import logging
import argparse

import requests
from zapv2 import ZAPv2

from config import config
from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import

LOG = logging.getLogger("ptscripts.zap_attack")


def run_zap_attack(url, zap):
    LOG.info('ZAP Attacking {}'.format(url))
    zap.urlopen(url)
    time.sleep(2)

    # spider
    scanid = zap.spider.scan(url)
    time.sleep(2)
    while (int(zap.spider.status(scanid)) < 100):
        LOG.info('Spider progress {}%'.format(zap.spider.status(scanid)))
        time.sleep(2)
    LOG.info('Spider completed for url: {}'.format(url))
    time.sleep(5)

    # forced browse

    # scan
    LOG.info('Starting scan of {}'.format(url))
    scanid = zap.ascan.scan(url)
    while (int(zap.ascan.status(scanid)) < 100):
        LOG.info('Scan progress {}%'.format(zap.ascan.status(scanid)))
        time.sleep(10)
    LOG.info('Scan completed')


def main(args):
    utils.dir_exists(args.output, True)

    zap = ZAPv2(apikey=config.ZAP_API, proxies=config.ZAP_PROXIES)  # pylint: disable=unexpected-keyword-arg
    # Create new session
    try:
        zap.core.new_session(args.output)
    except requests.exceptions.ProxyError:
        LOG.error("Couldn't attach to ZAP. Is it running?")
        return

    urls = utils.parse_webserver_urls(args.input)
    for url in urls:
        if not utils.check_url(url)[0]:
            continue
        run_zap_attack(url, zap)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='ZAP scan list of URLs.',
    )
    parser.add_argument('input', help='File with a URL each line.')
    parser.add_argument('output', help='Output directory where zap session will be created.')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Logger set to debug.")
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
