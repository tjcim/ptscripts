"""
Check the website headers for specific security-related headers.

USAGE: python security_headers.py <url> <output_dir>
"""
import os
import logging
import urllib3

import click
import requests

HEADERS = ['Strict-Transport-Security', 'X-Content-Type-Options',
           'X-Frame-Options', 'Content-Security-Policy',
           'X-Permitted-Cross-Domain-Policies', 'X-XSS-Protection']
RESULTS_FILE = "header_results.txt"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
WHITE = "\033[1;37m"
RESET = "\033[0m"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def write_results(output, present_headers, missing_headers):
    with open(os.path.join(output, RESULTS_FILE), "w") as fp:
        fp.write("Existing headers:\n")
        fp.write("*" * 17 + "\n")
        fp.write("\n".join([x["file_output"] for x in present_headers]) + "\n")
        fp.write("\nMissing headers:\n")
        fp.write("*" * 17 + "\n")
        fp.write("\n".join([x["file_output"] for x in missing_headers]) + "\n")
        fp.write("""
X-Frame-Options and X-XSS-Protection can be covered by a Content-Security-Policy that is locked down
                 """)


def get_headers(url):
    res = requests.get(url, verify=False)
    if res.status_code != 200:
        log.warning(f"{RED}We received a status code of {res.status_code}{RESET}")
    return res.headers


def process_headers(headers):
    present_headers = []
    missing_headers = []
    for header in HEADERS:
        data = {
            "name": header,
            "present": False,
            "bash_output": "",
            "file_output": "",
            "value": "",
        }
        if header in headers:
            data["present"] = True
            data["value"] = headers[header]
            data["bash_output"] = f"{GREEN}FOUND {header}: {data['value']}{RESET}"
            data["file_output"] = f"FOUND {header}: {data['value']}"
            present_headers.append(data)
        else:
            data["bash_output"] = f"{RED}MISSING {header}{RESET}"
            data["file_output"] = f"MISSING {header}"
            missing_headers.append(data)
        log.info(data["bash_output"])
    return present_headers, missing_headers


def csp_logic(present_headers, missing_headers):
    csp = [header for header in present_headers if header["name"] == "Content-Security-Policy"]
    xfo = [header for header in missing_headers if header["name"] == "X-Frame-Options"]
    xxp = [header for header in missing_headers if header["name"] == "X-XSS-Protection"]
    if csp:
        # Content-Security-Policy can cover the absence of X-Frame-Options
        # as long as the CSP is defined with a frame-src, frame-ancestors, child-src, or default-src
        # that is restrictive.
        if xfo:
            log.info((f"{WHITE}"
                      "X-Frame-Options may not be necessary."
                      " Check that the Content-Security-Policy is locked down."
                      f"{RESET}"
                      )
                     )
        # Content-Security-Policy can cover the absence of X-XSS-Protection
        # as long as the CSP is restrictive.
        if xxp:
            log.info((f"{WHITE}"
                      "X-XSS-Protection may not be necessary."
                      " Check that the Content-Security-Policy is locked down."
                      f"{RESET}"
                      )
                     )


def main(url, output):
    log.info("*" * 25)
    log.info(f"Running security_headers for {url}")
    headers = get_headers(url)
    present_headers, missing_headers = process_headers(headers)
    csp_logic(present_headers, missing_headers)
    write_results(output, present_headers, missing_headers)


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

log = logging.getLogger("ptscripts.security_headers")

if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
