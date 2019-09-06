"""
Extract vulnerabilities from testssl csvs to one file

USAGE: python parse_testssl.py <input_dir> <output_dir>
"""
import os
import re
import csv
import glob
import logging
import argparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.parse_testssl")
IGNORED = ['INFO', 'OK', 'WARN', 'DEBUG', 'LOW']


def get_ip(csv_file):
    m = re.search('_(.+?)_', csv_file)
    if m:
        ip = m.group(1)
    return ip


def get_port(csv_file):
    m = re.search('_(\d*)\.csv', csv_file)
    if m:
        port = m.group(1)
    return port


def extract_vulns(csv_file, file_dir, results_path):
    ip = get_ip(csv_file)
    port = get_port(csv_file)
    csv_path = os.path.join(file_dir, csv_file)
    LOG.info(f'Working on file: {csv_file}, ip: {ip}, port: {port}')
    vuln_count = 0
    vulns = []
    with open(csv_path) as csv_contents:
        csv_reader = csv.reader(csv_contents, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            if row[3] not in IGNORED:
                line_count += 1
                vuln_count += 1
                vulns.append([ip, port, row[0], row[1], row[3], row[4]])
    LOG.info(f'Found {vuln_count} vulnerabilities')
    results_file_path = os.path.join(results_path, 'testssl_results.csv')
    with open(results_file_path, mode='a') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for vuln in vulns:
            results_writer.writerow(vuln)
    return vuln_count


def main(args):
    # Find all csv files in folder
    results_file = os.path.join(args.output, 'testssl_results.csv')
    if os.path.isfile(results_file):
        LOG.warning('Results file already exists, deleting and creating it again.')
        os.remove(results_file)
    LOG.info(f'Processing all testssl csv files and saving vulnerabilities into {results_file}')
    with open(results_file, mode='w') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['IP', 'Port', 'Test ID', 'FQDN/IP', 'Risk Rating', 'Description'])
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
    parser.add_argument('input', help="full path to testssl folder.")
    parser.add_argument('output', help="where to store results")
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
