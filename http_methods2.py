import logging
import argparse
import http.client
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.nc_http_methods")


def check_debug(parsed_url):
    conn = http.client.HTTPSConnection(parsed_url.netloc, parsed_url.port)
    conn.request("DEBUG", parsed_url.path, headers={'Command': 'stop-debug'})
    r1 = conn.getresponse()
    print("DEBUG")
    print(r1.status, r1.reason)
    for line in r1.read().splitlines():
        print(line.decode('utf8'))


def main(args):
    parsed_url = urlparse(args.url)
    netloc = parsed_url.netloc
    conn = http.client.HTTPSConnection(netloc, parsed_url.port)
    for method in ["HEAD", "PUT", "DELETE", "TRACE", "OPTIONS", "CONNECT"]:
        conn.request(method, parsed_url.path)
        r1 = conn.getresponse()
        print(method)
        print(r1.status, r1.reason)
        for line in r1.read().splitlines():
            print(line.decode('utf8'))
    check_debug(parsed_url)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture http_methods data and image.',
    )
    parser.add_argument('url', help="url to be tested")
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


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
