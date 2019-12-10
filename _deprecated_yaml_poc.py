import os
import time
import stat
import logging
import argparse

import yaml

from config import config  # noqa
from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.yaml_poc")


def c_format(commands, args):
    for com in commands:
        com['command'] = com['command'].format(
            scripts_path=config.SCRIPTS_PATH,
            pentest_path=os.path.join(config.BASE_PATH, args.name + "/ept"),
            ip_file=args.ips_file,
            pentest_name=args.name,
            domain_name=args.domain,
        )


def c_print(commands):
    for com in commands:
        if com.get('help') and com['help']:
            print('# ' + com['help'])
        print(com['command'])


def c_write(commands, args):
    pentest_path = os.path.join(config.BASE_PATH, args.name + "/ept")
    commands_path = os.path.join(pentest_path, "yaml_commands.txt")
    script_path = os.path.join(pentest_path, "commands.sh")
    other_path = os.path.join(pentest_path, "not_scriptable.txt")
    with open(commands_path, "w") as f:
        f.write("## Commands file written on {} for {} using version {} ##\r\n\r\n".format(
            time.strftime('%I:%M%p %Z on %b %d, %Y'),
            args.name,
            config.VERSION,
        ))
        for com in commands:
            f.write(com['command'] + "\r\n")
            f.write("\r\n")
    with open(script_path, "w") as f:
        f.write("#!/usr/bin/env bash" + "\n")
        for com in commands:
            if com['scriptable']:
                f.write(com['command'] + "\n")
    with open(other_path, "w") as f:
        for com in commands:
            if not com['scriptable']:
                f.write(com['command'] + "\n")
    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)


def load_commands(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def get_name():
    return input('Pentest directory name? ')


def get_domain():
    return input('Domain to use for dnsdumpster and fierce? ')


def get_ips():
    return input('Name of ip file [ips.txt]: ') or 'ips.txt'


def main(args):
    if not args.name:
        args.name = get_name()
    if not args.domain:
        args.domain = get_domain()
    if not args.ips_file:
        args.ips_file = get_ips()
    commands_file = os.path.join(config.SCRIPTS_PATH, "commands/commands.yaml")
    commands = load_commands(commands_file)
    c_format(commands, args)
    c_print(commands)
    c_write(commands, args)


def parse_args(args):
    ips_path_prompt = os.path.join(config.BASE_PATH, "<short name>/ept")
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Print commands formatted for current pentest.',
    )
    parser.add_argument('-n', '--name', help="Short name of the engagement (folder name).")
    parser.add_argument('-d', '--domain', help="Root domain for the engagement (no www).")
    parser.add_argument('-i', '--ips-file', help="Relative path (from {}) to ips file provided for engagement.".format(ips_path_prompt))
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
