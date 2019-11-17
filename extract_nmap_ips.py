"""
Extract IPs from nmap scan.

The idea is that you use nmap -F (or similar) to scan fast. Then extract all the IPs found and use
a more complete nmap scan on the IPs.

The two instances I find this necessary:
* On some networks the hosts do not respond to Ping and therefore they won't get scanned
with Nmap without turning off Ping. If you do turn off Ping it can take forever to get
a comprehensive scan.

* I have also encoutered networks where a router or firewall will respond to every ping,
again a comprehensive scan will be slow because it will try to scan non-existent hosts.
"""
import os
import logging

import click

import nmap_to_csv as ntc


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


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-i", "--input", "input_path",
              help="Full path to nmap XML file.",
              type=click.File(mode="r"), prompt=True)
@click.option("-o", "--output", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def cli(verbocity, input_path, output):
    set_logging_level(verbocity)
    if not output:
        output_dir = os.path.dirname(input_path.name)
        output_path = os.path.join(output_dir, "nmap_found_ips.txt")
        log.info(f"Since no output file was specified the output file will be: {output_path}")
    log.info("Parsing nmap file.")
    hosts = ntc.parse_nmap(input_path)
    log.info("Writing out results.")
    with open(output_path, "w") as fp:
        for host in hosts:
            fp.write(f"{host['ipv4']}\n")
    log.info(f"Done. IPs writtent to {output_path}")


logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{", datefmt="%H:%M:%S",
)
log = logging.getLogger()

if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
