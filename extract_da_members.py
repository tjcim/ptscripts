"""
Reads the output from enum4linux -G and extracts all users in the Domain Admin group.

Arguments:
    input: path to results from enum4linux command
    output: path to save usernames
"""
import os
import logging

import click


GROUP_NAME = "Group 'Domain Admins'"


def get_usernames(input_path, group_text):
    users = []
    for line in input_path.readlines():
        if line.startswith(group_text):
            users.append(line.split()[-1])
    return users


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-i", "--input", "input_path", type=click.File(mode="r"), prompt=True)
@click.option("-o", "--output", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def cli(verbocity, input_path, output):
    set_logging_level(verbocity)
    if not output:
        output_dir = os.path.dirname(input_path.name)
        output_path = os.path.join(output_dir, "da_members.txt")
        log.info(f"Since no output file was specified the output file will be: {output_path}")
    users = get_usernames(input_path, GROUP_NAME)
    with open(output_path, "w") as fp:
        fp.write("\n".join(users))
        fp.write("\n")
    log.info(f"List of users with domain admins written to {output_path}")


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
