""" Formats the ports.csv file into a format for the reports. """
import os
import csv
import logging
import argparse

from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.format_nmap")


def write_nmap_results_csv(output_file, hosts):
    """ Write the parsed hosts to the csv file. """
    header = ["Host", "Port", "Protocol", "Name", "Information"]
    with open(output_file, "w", newline='') as f:
        csvwriter = csv.writer(f)
        # Write header
        csvwriter.writerow(header)
        # Write results
        for host in hosts:
            csvwriter.writerow([
                host["ipv4"], host["port"], host["protocol"],
                host["service_name"], host["product_name"]
            ])


def main(args):
    LOG.info("Reading in csv file: {}".format(args.input))
    results = utils.csv_to_dict(args.input)
    output_file = os.path.join(args.output, "ports_report.csv")
    LOG.info("Writing new file to: {}".format(output_file))
    write_nmap_results_csv(output_file, results)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Format the ports.csv file',
        prog='format_nmap.py',
    )
    parser.add_argument('input', help='Ports csv file to parse.')
    parser.add_argument('output', help='Output directory where file will be created.')
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


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
