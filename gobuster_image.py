"""
Run gobuster save data and create images of the results

USAGE: python gobuster_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import re
import os
import logging
import argparse
import requests
from urllib.parse import urlparse, urljoin

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.gobuster_image")
COMMAND = "gobuster -q dir -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u {url} -o gobuster_{domain}.txt"
EXC_COMMAND = "gobuster -q dir --exclude-length {exclude} -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u {url} -o gobuster_{domain}.txt"
CODE_COMMAND = "gobuster -q dir  --status-codes-blacklist {exclude_code},404 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u {url} -o gobuster_{domain}.txt"
PROXY_COMMAND = "gobuster dir -p {proxy} -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u {url}"
PROXIES = {
    "http": "127.0.0.1:8080",
    "https": "127.0.0.1:8080"
}


def read_gobuster_output(url: str, output_path: str) -> set :
    """Returns a set of URLs that were found."""
    regex = re.compile(r"^(\/.*?) .*\(Status: ([0-9]{3})\).*\[Size: [0-9]+\](?: \[--> (.*)\])?$")
    results = set(())
    with open(output_path, "r") as file_pointer:
        raw_output = file_pointer.readlines()
    for line in raw_output:
        line = line.strip()
        matches = regex.match(line)
        if matches:
            path, status, redirect_url = matches.groups()
            if redirect_url and redirect_url.startswith("/"):
                results.add(urljoin(url, redirect_url))
            elif redirect_url:
                results.add(redirect_url)
            else:
                results.add(urljoin(url, path))
    return results


def proxy_results(url: str, output_path: str) -> None :
    """Does a GET request using a proxy on each URL found by gobuster."""
    results = read_gobuster_output(url, output_path)
    LOG.info("Proxying found URLs in Burp")
    for item in results:
        LOG.info(f"Requesting: {item}")
        try:
            _ = requests.get(item, proxies=PROXIES, verify=False)
        except Exception:
            continue


def main(args):
    LOG.info("Running gobuster for {}".format(args.url))
    netloc = urlparse(args.url).netloc
    domain = netloc.split(":")[0]
    if args.proxy:
        command = PROXY_COMMAND.format(url=args.url, proxy=args.proxy)
    elif args.exclude:
        command = EXC_COMMAND.format(url=args.url, domain=domain, exclude=args.exclude)
    elif args.exclude_code:
        command = CODE_COMMAND.format(url=args.url, domain=domain, exclude_code=args.exclude_code)
    else:
        command = COMMAND.format(url=args.url, domain=domain)
    LOG.info(f"Running command: {command}")
    html_path = os.path.join(args.output, "gobuster_{}.html".format(domain))
    txt_path = os.path.join(args.output, f"gobuster_{domain}.txt")
    if not args.no_scan:
        text_output = run_commands.bash_command(command, True)
        html_output = run_commands.create_html_file(text_output, command, html_path)
        if html_output and args.screenshot:
            LOG.info("Creating a screenshot of the output and saving it to {}".format(args.screenshot))
            utils.dir_exists(args.screenshot, True)
            utils.selenium_image(html_output, args.screenshot)
        if not html_output:
            LOG.error("Didn't receive a response from running the command.")
    if args.burp:
        proxy_results(args.url, txt_path)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture gobuster data and image.',
    )
    parser.add_argument('url', help="url to be tested")
    parser.add_argument('output', help="where to store results")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshot will be saved.")
    parser.add_argument("-p", "--proxy",
                        help="Proxy")
    parser.add_argument("-b", "--burp", action="store_true", help="Once done, proxy all found URLs through burp.")
    parser.add_argument("-n", "--no-scan", action="store_true", help="Don't scan")
    parser.add_argument("-x", "--exclude", help="Exclude responses with this length")
    parser.add_argument("-y", "--exclude-code", help="Exclude responses with this code (plus 404)")
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
