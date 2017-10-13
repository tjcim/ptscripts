"""
Creates web_commands.txt file with common web app assessment commands.

Formats each command to output both to the screen and to an html file using aha.

Parameters
----------
name : string
    Folder name where the output will be stored. The name is joined to BASE_PATH set in config.py
url : string
    URL of the application
"""
import logging
import argparse

import utils
import logging_config  # noqa pylint: disable=unused-import


def parse_args():
    parser = argparse.ArgumentParser(parents=[utils.parent_argparser()])
    parser.add_argument("name", help="Pentest folder name. The output will be stored in BASE_PATH/<name> (BASE_PATH) configured in config.py")
    parser.add_argument("url", help="URL of application")
    args = parser.parse_args()
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == "__main__":
    log = logging.getLogger("ptscripts.web_commands")
    utils.print_commands(parse_args(), "web")
    log.info("blah")
