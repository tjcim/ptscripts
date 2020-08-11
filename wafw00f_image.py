"""
Run wafw00f save data and create images of the results

USAGE: python wafw00f_image.py <url> <output_dir> [-s <screenshot directory>]
"""
import os
import logging
from urllib.parse import urlparse

import click

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.wafw00f_image")


def main(output, url, no_screenshot, proxy):
    if proxy:
        command = "wafw00f -a -p {proxy} {url}".format(proxy=proxy, url=url)
    else:
        command = "wafw00f -a {url}".format(url=url)
    LOG.info("Running wafw00f command: {}".format(command))
    netloc = urlparse(url).netloc
    domain = netloc.split(":")[0]
    html_path = os.path.join(output, "wafw00f_{}.html".format(domain))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and not no_screenshot:
        screenshot_path = os.path.join(output, "screenshots")
        LOG.info("Creating a screenshot of the output and saving it to {}".format(screenshot_path))
        utils.dir_exists(screenshot_path, True)
        utils.selenium_image(html_output, screenshot_path)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
              help="Full path to pentest folder.")
@click.option("-u", "--url", prompt=True, help="URL to be checked.")
@click.option("-n", "--no-screenshot", is_flag=True, help="Do not save a screenshot")
@click.option("-p", "--proxy", help="Use a proxy to perform requests.")
def cli(verbocity, output, url, no_screenshot, proxy):
    set_logging_level(verbocity)
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
