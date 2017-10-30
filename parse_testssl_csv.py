"""
Parse and combine the testssl csv files into combined_issues.csv

Parameters
----------
input_dir : string
    Required - Full path to the directory in which the testssl csvs are located. Make sure no other csvs are present.
"""
import os
import logging
import argparse

from utils import utils
from models.models import TestSSLVulnerability


log = logging.getLogger("ptscripts.parse_testssl_csv")


def parse_testssl_output_for_issues(csv_file):
    results = []
    output = utils.csv_to_list(csv_file)
    for row in output:
        try:
            if row[3] not in ['INFO', 'OK', 'severity']:
                results.append(row)
        except IndexError:
            print('IndexError on row: {}'.format(row))
    return results


def get_issues(csv_dir):
    """ pull all the issues from the csv files. """
    issues = []
    csv_files = utils.find_files(csv_dir)
    for csv_file in csv_files:
        results = parse_testssl_output_for_issues(os.path.join(csv_dir, csv_file))
        for result in results:
            issues.append(result)
    return issues


def parse_testssl(args):
    # test if combined_issues.csv exists
    if os.path.isfile(os.path.join(args.input_dir, "combined_issues.csv")):
        log.error('Remove the combined_issues.csv file in {} before running.'.format(args.input_dir))
        return
    vulnerabilities = []
    issues = get_issues(args.input_dir)
    for issue in issues:
        # Check if we already have a vulnerability for this issue
        log.debug("Processing issue: {}".format(issue))
        if utils.find_vulnerability(vulnerabilities, issue[0]):
            log.debug("Vulnerability exists: {}".format(issue[0]))
            vuln = utils.find_vulnerability(vulnerabilities, issue[0])
            log.debug("Adding affected host to {} issue: {}".format(vuln, issue))
            vuln.add_affected(issue)
        else:
            log.debug("Vulnerability does not exist: {}".format(issue[0]))
            log.debug("Creating vulnerability: finding={}, risk_level={}, _id={}".format(issue[4], issue[3], issue[0]))
            vuln = TestSSLVulnerability(issue[4], issue[3], issue[0])
            log.debug("Adding affected host {}".format(issue))
            vuln.add_affected(issue)
            vulnerabilities.append(vuln)
    output_vulns = [[
        "Finding", "Affected Device/Technology", "Risk Level", "Business Impact",
        "Remediation Procedure", "Resource Required",
    ]]
    for vuln in vulnerabilities:
        output_vulns.append(vuln.list_format())
    out_csv = os.path.join(args.input_dir, "combined_issues.csv")
    utils.write_list_to_csv(output_vulns, out_csv)


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()], prog='parse_testssl_csv.py',
        description='Parses and combines the testssl vulnerabilities.')
    parser.add_argument('input_dir', help='Directory with testssl output.')
    args = parser.parse_args()
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    parse_testssl(parse_args())
