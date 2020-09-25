"""
Run testssl save data and create images of the results

USAGE: python mtestssl.py <output_dir> --url <url>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import sys
import logging
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

import click

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.mtestssl")


def run_testssl(url, output, no_screenshot, proxy):
    if not utils.uses_encryption(url):
        return
    parsed_url = urlparse(url)
    port = '443'
    if parsed_url.port:
        port = str(parsed_url.port)
    html_path = os.path.join(output, f"testssl_{parsed_url.netloc}_{port}.html")
    csv_output = os.path.join(output, f"testssl_{parsed_url.netloc}_{port}.csv")
    if os.path.isfile(csv_output):
        LOG.info("CSV file already exists, deleting it.")
        os.remove(csv_output)
    if proxy:
        command = f"testssl --warnings off --csvfile {csv_output} --proxy {proxy} {url}"
    else:
        command = f"testssl --warnings off --csvfile {csv_output} {url}"
    LOG.info('Running command: {}'.format(command))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and not no_screenshot:
        screenshot_path = os.path.join(output, "screenshots")
        LOG.info("Creating a screenshot of the output and saving it to {}".format(screenshot_path))
        utils.dir_exists(screenshot_path, True)
        utils.selenium_image(html_output, screenshot_path)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def main(output, url, no_screenshot, proxy):
    run_testssl(url, output, no_screenshot, proxy)


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
              help="Full path to pentest folder.")
@click.option("-u", "--url", help="URL to be checked.")
@click.option("-l", "--list", "url_list", help="List of URLs to run against.")
@click.option("-n", "--no-screenshot", is_flag=True, help="Do not save a screenshot")
@click.option("-p", "--proxy", "proxy", help="Use a proxy")
def cli(verbocity, output, url, no_screenshot, proxy, url_list):
    set_logging_level(verbocity)
    if not os.path.isdir(output):
        try:
            os.mkdir(output)
        except Exception as e:
            log.critical(e)
            sys.exit(-1)
    if not url and not url_list:
        log.info("Either provide a URL or a list of URLs")
        sys.exit(-1)
    if url_list and os.path.isfile(url_list):
        log.info("Reading URL list.")
        with open(url_list, "r") as f:
            urls = f.readlines()
        for url in urls:
            main(output, url, no_screenshot, proxy)
    else:
        main(output, url, no_screenshot, proxy)


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
