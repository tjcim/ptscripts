#!/usr/bin/env python
"""
"""
import os
import json
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
log = logging.getLogger()


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
        with open(file_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
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
        js_files.append(download_file(url, download_dir))
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


def eslint_files(eslint_exe, beautified_dir, eslintrc_path):
    log.info(f"Running eslint against: {beautified_dir}")
    data = {
        "env": {
            "browser": True
        }
    }
    with open(eslintrc_path, 'w') as f:
        json.dump(data, f)
    command = f"eslint {beautified_dir}"
    res = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("\n" + res.stdout.decode())
    log.info("Finished running eslint")


def semgrep_files(semgrep_exe, semgrep_config, beautified_dir):
    log.info(f"Running semgrep against: {beautified_dir}")
    command = f'semgrep --config {semgrep_config} {beautified_dir}'
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
@click.option("-s", "--semgrep-config", default="https://semgrep.dev/p/r2c-security-audit")
def cli(verbocity, js_file, semgrep_config):
    set_logging_level(verbocity)
    base_dir = pathlib.Path(js_file).parent.resolve()
    download_dir = os.path.join(base_dir, "downloads")
    beautified_dir = os.path.join(base_dir, "beautified")
    eslintrc_path = os.path.join(base_dir, ".eslintrc.json")
    download_js_files(js_file, download_dir)
    beautified_dir = beautify_js_files(download_dir, beautified_dir)
    eslint_exe = which("eslint")
    if eslint_exe:
        eslint_files(eslint_exe, beautified_dir, eslintrc_path)
    else:
        log.warning("Could not find eslint in PATH. Eslint will not be run.")
    semgrep_exe = which("semgrep")
    if semgrep_exe:
        semgrep_files(semgrep_exe, semgrep_config, beautified_dir)
    else:
        log.warning("Could not find semgrep in PATH. Semgrep will not be run.")


if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
