#!/usr/bin/env python
"""
Tests the website against a list of potentially dangerous HTTP Methods

Arguments:
    output: path to pentest folder
        The output of this script will be saved to {output}/http_methods
        The folder will be created if it doesn't exist.

    url: Full url to the web app being tested.
        It should include subdomains and folders if present. It should also include the port
        if required and start with http or https.

Example: http_methods.py -o /root/pentests/acme/ -u https://www.acme.org/
"""
import os
import logging
import http.client
from urllib.parse import urlparse

import click

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


METHODS = ["HEAD", "DEBUG", "PUT", "DELETE", "TRACE", "OPTIONS", "CONNECT", "PROPFIND"]
IGNORE_STATUS = [400, 401, 403, 405, 501]


def get_response(conn, parsed_url, method, path):
    log.debug(f"Checking method: {method}")
    if method == "DEBUG":
        conn.request("DEBUG", parsed_url.path, headers={'Command': 'stop-debug'})
    else:
        conn.request(method, path)
    try:
        r1 = conn.getresponse()
    except http.client.RemoteDisconnected:
        log.debug(f"Method: {method} was disconnected without a response.")
        return
    log.debug(f"{method} Connection response status: {r1.status}, reason: {r1.reason}")
    response = r1.read()
    if r1.status in IGNORE_STATUS:
        log.info(f"{method}: return a status of {r1.status} and will be ignored.")
        return
    if not response:
        log.debug(f"{method} provided no response.")
        return
    log.info(f"{method}: returned a response of {len(response)} with a status of {r1.status}")
    return response


def main(output, url):
    print("*" * 20)
    print("Running http_methods.py")
    print(f"Testing {url} against a list of potentially dangerous HTTP Methods.")
    print(f"Methods we are testing: {', '.join(METHODS)}")
    print(f"Saving any content received from these methods to {output}/http_methods/")
    print("*" * 20)
    found_methods = []
    methods_folder = os.path.join(output, "http_methods")
    os.makedirs(methods_folder, exist_ok=True)
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if not parsed_url.path:
        path = "/"
    else:
        path = parsed_url.path
    if parsed_url.scheme == 'https':
        conn = http.client.HTTPSConnection(netloc)
    else:
        conn = http.client.HTTPConnection(netloc)
    for method in METHODS:
        response = get_response(conn, parsed_url, method, path)
        if not response:
            continue
        found_methods.append(method)
        method_file = os.path.join(methods_folder, method + "_method_check.html")
        with open(method_file, "w") as fp:
            for line in response.splitlines():
                fp.write(line.decode('utf8') + "\n")
    print("*" * 20)
    if len(found_methods) > 0:
        print(f"Done. We found these methods that need further investigation: {', '.join(found_methods)}")
    else:
        print(f"Done. No methods need further investigation.")
    print("*" * 20)


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
              help="Full path to pentest folder.")
@click.option("-u", "--url", prompt=True, help="URL to be checked.")
def cli(verbocity, output, url):
    set_logging_level(verbocity)
    main(output, url)


def set_logging_level(verbocity):
    if verbocity == "verbose":
        log.setLevel("DEBUG")
        log.debug("Setting logging level to DEBUG")
    elif verbocity == "quiet":
        log.setLevel("ERROR")
        log.error("Setting logging level to ERROR")
    else:
        log.setLevel("INFO")
        log.info("Setting logging level to INFO")


log = logging.getLogger("ptscripts.http_methods")


if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
