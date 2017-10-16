"""
Creates web commands file with common web app assessment commands.

Formats each command to output both to the screen and to an html file using aha.

Parameters
----------
output_dir : string
    Required - Folder name where the output from each of the commands are stored.
output_file : string
    Required - Full path to where the output from this script is saved.
url : string
    Required - URL of the application

Output
------
This will save a text file named [output_file] with a bunch of commands to run against [url].

Usage
-----
python web_commands.py /root/pentests/test /root/pentests/test/web_commands.txt http://www.sample.org

"""
import sys
import logging
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from ptscripts import utils
import ptscripts.logging_config  # noqa pylint: disable=unused-import
from ptscripts import config
from ptscripts.commands import COMMANDS


ASSESSMENT_TYPES = {
    "web": "Web Application Assessment",
    "pentest": "External Pentest",
}


def print_commands(args, assessment_type):
    log = logging.getLogger("ptscripts.web_commands.print_commands")
    netloc = urlparse(args.url).netloc
    log.debug("netloc: " + netloc)
    folder_path = args.output_dir
    file_path = args.output_file
    log.debug("file_path: " + file_path)
    log.info("Writing header information.")
    with open(file_path, 'w') as file_handler:
        header = "# {assessment_type} commands created using version {version}\r\n"
        header_text = header.format(
            assessment_type=ASSESSMENT_TYPES[assessment_type],
            version=config.VERSION
        )
        file_handler.write(header_text)
        file_handler.write("#" + ("*" * len(header)) + "\r\n\r\n")
    for command_item in COMMANDS:
        if assessment_type not in command_item["tags"]:
            log.debug("{} not found in {}.".format(assessment_type, command_item["tags"]))
            continue
        log.info("Writing {} command".format(command_item["name"]))
        formatted_command = command_item["command"].format(
            url=args.url, output_dir=folder_path, netloc=netloc, scripts_dir=config.SCRIPTS_PATH)
        with open(file_path, 'a') as file_handler:
            try:
                log.debug("Writing comments: {}".format(command_item["comments"]))
                for comment in command_item["comments"]:
                    if comment:
                        file_handler.write("# {}\r\n".format(comment))
            except KeyError:
                # No comments
                pass
            log.debug("Writing command: {}".format(formatted_command))
            file_handler.write("{}\r\n\r\n".format(formatted_command))
    log.info("All commands written.")


def main(args):
    print_commands(args, "web")


def parse_args(args):
    parser = argparse.ArgumentParser(parents=[utils.parent_argparser()])
    parser.add_argument("output_dir", help="Full path to where the output of the commands should be saved.")
    parser.add_argument("output_file", help="Full path and name of the output from this script.")
    parser.add_argument("url", help="URL of application")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
