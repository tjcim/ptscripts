#!/usr/bin/env python
"""
Sets up the initial folders and creates the command list for an internal pentest.

Arguments:
    output: path to pentest folder
        The pentest root folder will be created below this level. Typically I will do
        /root/pentests/<company name> as the output.
"""
import os
import stat
import glob
import time
import shutil
import logging

import yaml
import click
from jinja2 import Template


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RC_TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "rc_files")
VERSION = "0.3"


def create_render_args(pentest_name, ipt_dir, host):
    nmap_xml = os.path.join(ipt_dir, "nmap/ss_all.xml")
    render_args = {
        'name': pentest_name,
        'nmap_xml': nmap_xml,
        'host': host,
    }
    return render_args


def render_rc_files(rc_folder, render_args):
    log.info("Creating RC files.")
    templates = glob.glob(RC_TEMPLATES_DIR + "/*.j2")
    for template in templates:
        with open(template, "r") as fp:
            content = Template(fp.read())
        rendered = content.render(render_args)
        # go from /opt/ptscripts/rc_files/db_import.rc.j2 to db_import.rc
        rc_file_name = os.path.split(template)[1][:-3]
        with open(os.path.join(rc_folder, rc_file_name), "w") as fp:
            fp.write(rendered)
    log.info("RC files created.")


def checklist(ipt_dir):
    src = os.path.join(SCRIPT_DIR, "templates/int_checklist.txt")
    dst = os.path.join(ipt_dir, "checklist.txt")
    log.info("Writing checklist file to: {}".format(dst))
    shutil.copyfile(src, dst)


def load_commands(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def commands_format(commands, ipt_dir, pentest_name, host):
    for com in commands:
        com['command'] = com['command'].format(
            scripts_path=SCRIPT_DIR,
            pentest_path=ipt_dir,
            pentest_name=pentest_name,
            host=host,
        )


def create_command_file(ipt_dir, pentest_name, host):
    log.info("Creating commands files.")
    commands_yaml = os.path.join(SCRIPT_DIR, "commands/int_commands.yaml")
    commands = load_commands(commands_yaml)
    commands_format(commands, ipt_dir, pentest_name, host)
    commands_write(commands, ipt_dir, pentest_name)
    log.info("Done creating command files.")


def commands_write(commands, ipt_dir, pentest_name):
    log.info("Writing commands files.")
    commands_path = os.path.join(ipt_dir, "yaml_commands.txt")
    script_path = os.path.join(ipt_dir, "commands.sh")
    other_path = os.path.join(ipt_dir, "not_scriptable.txt")
    with open(commands_path, "w") as f:
        f.write("## Commands file written on {} for {} using version {} ##\r\n\r\n".format(
            time.strftime('%I:%M%p %Z on %b %d, %Y'),
            pentest_name,
            VERSION,
        ))
        for com in commands:
            f.write(com['command'] + "\r\n")
            f.write("\r\n")
    log.info(f"Commands written to {commands_path}")
    with open(script_path, "w") as f:
        f.write("#!/usr/bin/env bash" + "\n")
        for com in commands:
            if com['scriptable']:
                f.write(com['command'] + "\n")
    log.info(f"Commands bash script written to {script_path}")
    with open(other_path, "w") as f:
        for com in commands:
            if not com['scriptable']:
                f.write(com['command'] + "\n")
    log.info(f"Writing non-scriptable commands to {other_path}")
    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)
    log.info("Bash script set as executable")


def create_directories(ipt_dir):
    log.info("Creating pentest directories.")
    pt_dirs = ["testssl", "whatweb", "rc_files", "nmap", "screenshots", "theharvester"]
    log.debug("Creating directory: {}".format(ipt_dir))
    os.makedirs(ipt_dir, exist_ok=True)
    for pt_dir in pt_dirs:
        pt_path = os.path.join(ipt_dir, pt_dir)
        log.debug("Creating directory: {}".format(pt_path))
        os.makedirs(pt_path, exist_ok=True)
    log.info("Directories have been created.")


def main(output, host):
    ipt_dir = os.path.join(output, "ipt")
    create_directories(ipt_dir)
    pentest_name = os.path.split(output)[1]
    if pentest_name is None:
        pentest_name = os.path.split(os.path.split(output)[0])[1]
    rc_folder = os.path.join(ipt_dir, "rc_files")
    render_args = create_render_args(pentest_name, ipt_dir, host)
    os.makedirs(rc_folder, exist_ok=True)
    render_rc_files(rc_folder, render_args)
    checklist(ipt_dir)
    create_command_file(ipt_dir, pentest_name, host)
    log.info(f"Folders, files, and scripts have been created in {ipt_dir}")


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(file_okay=False, dir_okay=True, resolve_path=True),
              help="Full path to pentest folder.")
@click.option("-h", "--host", prompt=True, help="Name of remote host (should be in .ssh/config).")
def cli(verbocity, output, host):
    set_logging_level(verbocity)
    main(output, host)


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
