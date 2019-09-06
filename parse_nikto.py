"""
Extract vulnerabilities from nikto csvs to one file

USAGE: python parse_nikto.py <input_dir> <output_dir>
"""
import os
import csv
import glob
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.parse_nikto")


def extract_vulns(csv_file, file_dir, results_path):
    csv_path = os.path.join(file_dir, csv_file)
    LOG.info(f'Working on file: {csv_file}')
    vuln_count = 0
    vulns = []
    with open(csv_path) as csv_contents:
        csv_reader = csv.reader(csv_contents, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # ignore first row
                line_count += 1
                continue
            vuln_count += 1
            vulns.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
    LOG.info(f'Found {vuln_count} vulnerabilities')
    results_file_path = os.path.join(results_path, 'nikto_results.csv')
    with open(results_file_path, mode='a') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for vuln in vulns:
            results_writer.writerow(vuln)
    return vuln_count


def main(args):
    # Find all csv files in folder
    results_file = os.path.join(args.output, 'nikto_results.csv')
    if os.path.isfile(results_file):
        LOG.warning('Results file already exists, deleting and creating it again.')
        os.remove(results_file)
    LOG.info(f'Processing all nikto csv files and saving vulnerabilities into {results_file}')
    with open(results_file, mode='w') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['Domain', 'IP', 'Port', 'ID', 'Method', 'Path', 'Description'])
    os.chdir(args.input)
    file_count = 0
    total_vulns = 0
    for csv_file in glob.glob("*.csv"):
        file_count += 1
        vuln_count = extract_vulns(csv_file, args.input, args.output)
        total_vulns += vuln_count
    LOG.info(f'Processed {file_count} csv files and found {total_vulns} vulnerabilities')


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Extract vulns from csv files.',
    )
    parser.add_argument('input', help="full path to nikto folder.")
    parser.add_argument('output', help="full path to directory to store results")
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
