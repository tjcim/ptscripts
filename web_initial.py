#!/usr/bin/env python
"""
Sets up the initial folders and creates the command list for the web app provided.

Arguments:
    output: path to pentest folder
        The web app pentest root folder will be created below this level. Typically I will do
        /root/pentests/<company name> as the output. This will create a folder for the web app
        at /root/pentests/<company name>/<web app including subdomain>/

    url: Full url to the web app being tested.
        It should include subdomains and folders if present. It should also include the port
        if required and start with http(s).
"""
import os
import stat
import shutil
import logging
from urllib.parse import urlparse

import yaml
import click

from config import config


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def format_commands(commands, url, base_path, netloc, proxy, burp):  # pylint: disable=too-many-locals
    log.info("Formatting commands")
    for com in commands:
        if proxy:
            command_text = com.get('proxy', com['command'])
        elif burp:
            command_text = com.get('burp', com['command'])
        else:
            command_text = com['command']
        com['command'] = command_text.format(
            scripts_path=SCRIPT_DIR,
            pentest_path=base_path,
            url=url,
            netloc=netloc,
            proxy=proxy,
        )


def print_commands(commands):
    log.info("Printing commands.")
    for com in commands:
        if com['command'] == "":
            continue
        if com.get('help') and com['help']:
            print('# ' + com['help'])
        print(com['command'])


def write_commands(commands, base_path, netloc):
    commands_path = os.path.join(base_path, f"web_commands_{netloc}.txt")
    scripts_path = os.path.join(base_path, f"wc_{netloc}.sh")
    log.info("Writing commands to txt file.")
    with open(commands_path, "w") as f:
        for com in commands:
            if com['command'] == "":
                continue
            f.write(com['command'] + "\n")
            f.write("\n")
    log.info("Writing commands to sh file.")
    with open(scripts_path, "w") as f:
        f.write("#!/bin/bash\n")
        for com in commands:
            if com['command'] == "":
                continue
            f.write(com['command'] + "\n")
    log.info("Marking bash script as executeable")
    st = os.stat(scripts_path)
    os.chmod(scripts_path, st.st_mode | stat.S_IEXEC)


def load_commands(yaml_file):
    with open(yaml_file, "r") as f:
        yaml_text = yaml.safe_load(f)
    return yaml_text


def create_checklists(pentest_dir):
    src = os.path.join(config.SCRIPTS_PATH, "templates/web_checklist.txt")
    dst = os.path.join(pentest_dir, "web_checklist.txt")
    log.info("Writing checklist file to: {}".format(dst))
    shutil.copyfile(src, dst)
    src = os.path.join(config.SCRIPTS_PATH, "templates/web_workflow.txt")
    dst = os.path.join(pentest_dir, "web_workflow.txt")
    log.info("Writing workflow file to: {}".format(dst))
    shutil.copyfile(src, dst)


def create_dirs(url, output):
    base_dirs = [
        "burp_zap", "screenshots",
    ]
    site_directory_name = urlparse(url).netloc.split(":")[0]
    base_path = os.path.join(output, site_directory_name)
    log.info("Creating directories")
    for directory in base_dirs:
        dir_path = os.path.join(base_path, directory)
        log.debug("Creating directory: {}".format(dir_path))
        os.makedirs(dir_path, exist_ok=True)
    log.info("Directories have been created.")
    return base_path, site_directory_name


def main(url, output, proxy, dont, burp):
    if dont:
        log.info("Not making any changes, just printing the formatted results.")
        site_directory_name = urlparse(url).netloc.split(":")[0]
        base_path = os.path.join(output, site_directory_name)
    else:
        base_path, site_directory_name = create_dirs(url, output)
        create_checklists(base_path)
    commands_file = os.path.join(SCRIPT_DIR, "commands/web_commands.yaml")
    commands = load_commands(commands_file)
    format_commands(commands, url, base_path, site_directory_name, proxy, burp)
    print_commands(commands)
    if not dont:
        write_commands(commands, base_path, site_directory_name)
    log.info(f"All done. Check the folder {base_path} for created files.")


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
@click.option("-p", "--proxy", "proxy", help="If a proxy is required, set it with this option")
@click.option("-b", "--burp", "burp", is_flag=True,
              help="Use burp")
@click.option("-d", "--dont", "dont", is_flag=True,
              help="Don't make any changes, just print out the commands")
def cli(verbocity, url, output, proxy, dont, burp):
    set_logging_level(verbocity)
    main(url, output, proxy, dont, burp)


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
