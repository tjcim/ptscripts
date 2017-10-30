import os
import logging
import argparse
from urllib.parse import urlparse

import yaml

from config import config  # noqa
from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.yaml_web")


def c_format(commands, args):
    for com in commands:
        com['command'] = com['command'].format(
            scripts_path=config.SCRIPTS_PATH,
            pentest_path=os.path.join(config.BASE_PATH, args.name),
            url=args.url,
        )


def c_print(commands):
    for com in commands:
        if com.get('help') and com['help']:
            print('# ' + com['help'])
        print(com['command'])


def c_write(commands, args):
    parsed_url = urlparse(args.url)
    netloc = parsed_url.netloc
    pentest_path = os.path.join(config.BASE_PATH, args.name)
    commands_path = os.path.join(pentest_path, "web_commands_{netloc}.txt".format(netloc=netloc))
    with open(commands_path, "w") as f:
        for com in commands:
            f.write(com['command'] + "\r\n")
            f.write("\r\n")


def load_commands(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def get_name():
    return input('Pentest directory name? ')


def get_url():
    return input('URL? ')


def main(args):
    if not args.name:
        args.name = get_name()
    if not args.url:
        args.url = get_url()
    commands = load_commands("commands/web_commands.yaml")
    c_format(commands, args)
    c_print(commands)
    c_write(commands, args)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Print web commands formatted for current pentest.',
    )
    parser.add_argument('-n', '--name', help="Short name of the engagement.")
    parser.add_argument('-u', '--url', help="URL for the engagement.")
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
