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
import os
import logging
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from config import config
from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import
from commands.commands import COMMANDS


ASSESSMENT_TYPES = {
    "web": "Web Application Assessment",
    "pentest": "External Pentest",
}


def write_header(file_path, assessment_type, version):
    """ Writes the header informatoin to the file. """
    header = [
        "# {} commands created using version {}".format(ASSESSMENT_TYPES[assessment_type], version),
        "#**************************************************************\r\n",
    ]
    with open(file_path, 'w') as file_handler:
        file_handler.write("\r\n".join(header))


def filter_commands(cmds, assessment_type):
    commands = [c for c in cmds if assessment_type in c["tags"]]
    return commands


def format_commands(commands, url, output_dir, netloc):
    for command in commands:
        command["formatted"] = command["command"].format(
            url=url, output_dir=output_dir, netloc=netloc,
            scripts_dir=config.SCRIPTS_PATH
        )
    return commands


def print_format_commands(commands):
    print_formatted = ""
    for command in commands:
        # Blank line before the command
        print_formatted += "\r\n\r\n"
        if "comments" in command and command["comments"]:
            for comment in command["comments"]:
                # Comments start with a '#' and are right above command.
                print_formatted += "# {}\r\n".format(comment)
        print_formatted += command["formatted"]
    return print_formatted


def main(args):
    assessment_type = "web"
    log = logging.getLogger("ptscripts.web_commands.print_commands")
    netloc = urlparse(args.url).netloc
    log.debug("netloc: " + netloc)
    file_path = os.path.join(args.output_dir, "{}_commands.txt".format(assessment_type))
    log.debug("file_path: " + file_path)
    log.info("Writing header information.")
    write_header(file_path, assessment_type, config.VERSION)
    # Filter for assessment type
    commands = filter_commands(COMMANDS, assessment_type)
    # Format command
    commands = format_commands(commands, args.url, args.output_dir, netloc)
    # Print format commands
    print_ready = print_format_commands(commands)
    with open(file_path, 'a') as f:
        f.write(print_ready)


def parse_args(args):
    parser = argparse.ArgumentParser(parents=[utils.parent_argparser()])
    parser.add_argument("output_dir", help="Full path to where the output of the commands should be saved.")
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
    import sys
    main(parse_args(sys.argv[1:]))
