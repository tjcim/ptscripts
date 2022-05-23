#!/usr/bin/env python
"""
Performs a security scan against a list of JavaScript files.

    The script will download the JavaScript files. It will use jsbeautifier to
    fix up the files. It will then scan them with semgrep.

    It will create two directories in the same folder where the text file is placed
    The two directories will be downloads and beautified.

Usage:
    Create a text file with the URLs of all the JavaScript files that should be scanned.

    python scan_js_files.py -f /path/to/list/of/urls
"""
import os
# import json
import pathlib
import logging
import subprocess

import click
import requests
import jsbeautifier


logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{", datefmt="%H:%M:%S",
)
log = logging.getLogger("ptscripts.scan_js_files")


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


def download_file(url, directory):
    local_filename = url.split('/')[-1]
    file_path = os.path.join(directory, local_filename)
    log.info(f"Downloading {url} to {file_path}")
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        log.warning(f"Received {str(resp.status_code)} for {url}")
        return None
    with open(file_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return file_path


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def create_dir(dir_path):
    log.debug("Creating directory: {dir_path}")
    os.makedirs(dir_path, exist_ok=True)


def download_js_files(js_file, download_dir):
    """
    Downloads each JS file listed in `js_file`.
    """
    create_dir(download_dir)
    urls = set()
    with open(js_file, 'r') as f:
        for line in f:
            urls.add(line.strip())
    log.info(f"Downloading {len(urls)} files")
    js_files = []
    for url in urls:
        js_path = download_file(url, download_dir)
        if js_path:
            js_files.append(js_path)
        else:
            log.warning(f"I was unable to download {url}")
    log.info("All files downloaded.")
    return download_dir


def beautify_js_files(download_dir, beautified_dir):
    log.info("Beautifying JS files")
    create_dir(beautified_dir)
    downloaded_files = pathlib.Path(download_dir).iterdir()
    opts = jsbeautifier.default_options()
    opts.end_with_newline = True
    for in_file in downloaded_files:
        if not in_file.suffix == '.js':
            continue
        out_path = os.path.join(beautified_dir, in_file.name)
        with open(in_file, 'r') as f:
            res = jsbeautifier.beautify_file(in_file, opts)
        with open(out_path, 'w') as f:
            f.write(res)
    log.info("All files have been beautified")
    return beautified_dir


def semgrep_files(semgrep_config, beautified_dir):
    log.info(f"Running semgrep against: {beautified_dir}")
    file_paths = [f for f in os.listdir(beautified_dir) if os.path.isfile(os.path.join(beautified_dir, f))]
    for file_path in file_paths:
        full_path = os.path.join(beautified_dir, file_path)
        command = f"""semgrep scan --config p/r2c-security-audit --config p/xss \
--config p/command-injection --config p/headless-browser --config p/jwt \
--config p/secrets --timeout 0 --timeout-threshold 0 --max-target-bytes 0 {full_path}"""
        log.info(f"Running command: {command}")
        res = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("\n" + res.stdout.decode())
    log.info("Finished running semgrep")


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-f", "--file", "js_file", prompt=True,
              help="Full path to the text file that contains the list of JS files to download and scan.")
@click.option("-s", "--semgrep-config", default='--config p/r2c-security-audit --config p/xss --config p/command-injection --config p/headless-browser --config p/jwt --config p/secrets')
def cli(verbocity, js_file, semgrep_config):
    set_logging_level(verbocity)
    base_dir = pathlib.Path(js_file).parent.resolve()
    download_dir = os.path.join(base_dir, "downloads")
    beautified_dir = os.path.join(base_dir, "beautified")
    download_js_files(js_file, download_dir)
    beautified_dir = beautify_js_files(download_dir, beautified_dir)
    semgrep_files(semgrep_config, beautified_dir)


if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
