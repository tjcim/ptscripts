"""
Check the website headers for specific security-related headers.

USAGE: python security_headers.py <url> <output_dir>
"""
import os
import logging

import click
import requests

HEADERS = ['Strict-Transport-Security', 'X-Content-Type-Options',
           'X-Frame-Options', 'Content-Security-Policy',
           'X-Permitted-Cross-Domain-Policies']
RESULTS_FILE = "header_results.txt"


def main(url, output):
    log.info(f"Running security_headers for {url}")
    res = requests.get(url)
    present_headers = []
    missing_headers = []
    for header in HEADERS:
        if header in res.headers:
            result_text = f"{header}: {res.headers[header]}"
            log.info(result_text)
            present_headers.append(result_text)
        else:
            missing_text = f"{header}"
            log.info(missing_text)
            missing_headers.append(missing_text)
    with open(os.path.join(output, RESULTS_FILE), "w") as fp:
        fp.write("Existing headers:\n")
        fp.write("*" * 17 + "\n")
        for item in present_headers:
            fp.write(item + "\n")
        fp.write("\nMissing headers:\n")
        fp.write("*" * 16 + "\n")
        for item in missing_headers:
            fp.write(item)
            if not item == missing_headers[-1]:
                fp.write("\n")


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-u", "--url", "url", prompt=True,
              help="Full url for the web application including virtual directories and port.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
              help="Full path to pentest folder.")
def cli(verbocity, url, output):
    set_logging_level(verbocity)
    main(url, output)


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


logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{", datefmt="%H:%M:%S",
)
log = logging.getLogger()

if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
