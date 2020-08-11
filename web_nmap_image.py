"""
Run nmap save data and create images of the results

USAGE: python web_nmap_image.py <output_dir> <input_file> [-s <screenshot directory>]
"""
import os
import logging

import click

from utils import utils, logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


LOG = logging.getLogger("ptscripts.web_nmap_image")


def main(output, url, no_screenshot, proxy):
    os.makedirs(output, exist_ok=True)
    output_dir = output
    output = os.path.join(output, "nmap_sT_common_{}".format(url))
    if proxy:
        command = """nmap -sT --proxy-type socks5h --proxy {proxy} -oA {output} {url}""".format(
            output=output, url=url, proxy=proxy)
    else:
        command = """nmap -sT -oA {output} {url}""".format(
            output=output, url=url)
    LOG.info("Running the command: {}".format(command))
    file_name = "nmap_sT_common_{}.html".format(url)
    html_path = os.path.join(output_dir, file_name)
    LOG.info("Saving output to: {}".format(html_path))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and not no_screenshot:
        screenshot_path = os.path.join(output_dir, "screenshots")
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
@click.option("-u", "--url-hostname", "url", prompt=True, help="Hostname to be checked.")
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
