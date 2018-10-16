"""
Parse and combine the testssl csv files into combined_issues.csv

Parameters
----------
input_dir : string
    Required - Full path to the directory in which the testssl csvs are located. Make sure no other csvs are present.
"""
import os
import csv
import logging
import argparse

from utils import utils
from models.models import TestSSLVulnerability


log = logging.getLogger("ptscripts.parse_testssl_csv")


def filter_issue(issue):
    try:
        if issue['severity'] not in ['INFO', 'OK', 'DEBUG']:
            return issue
    except KeyError:
        log.error("No severity found for issue.")


def parse_testssl_output_for_issues(filepath):
    results = []
    log.info(f'Processing file: {filepath}')
    with open(filepath, newline='') as csvfile:
        # reader = csv.DictReader(csvfile, fieldnames=['id', 'fqdn/ip', 'port', 'severity', 'finding'])
        reader = csv.DictReader(csvfile)
        for row in reader:
            if filter_issue(row):
                results.append(row)
    return results


def get_issues(csv_dir):
    """ pull all the issues from the csv files. """
    issues = []
    csv_files = utils.find_files(csv_dir)
    file_count = len(csv_files)
    for csv_file in csv_files:
        results = parse_testssl_output_for_issues(os.path.join(csv_dir, csv_file))
        for result in results:
            issues.append(result)
    return issues, file_count


def create_vulnerabilities(issues):
    vuln_hosts = set()
    vulnerabilities = []
    for issue in issues:
        # Check if we already have a vulnerability for this issue
        log.debug("Processing issue: {}".format(issue))
        vuln_hosts.add(issue['fqdn/ip'].split('/')[1])
        if utils.find_vulnerability(vulnerabilities, issue['id']):
            log.debug("Vulnerability exists: {}".format(issue['id']))
            vuln = utils.find_vulnerability(vulnerabilities, issue['id'])
            log.debug("Adding affected host to {} issue: {}".format(vuln, issue))
            vuln.add_affected(issue)
        else:
            log.debug("Vulnerability does not exist: {}".format(issue['id']))
            log.debug("Creating vulnerability: finding={}, risk_level={}, _id={}".format(issue['finding'], issue['severity'], issue['id']))
            vuln = TestSSLVulnerability(issue['finding'], issue['severity'], issue['id'])
            log.debug("Adding affected host {}".format(issue))
            vuln.add_affected(issue)
            vulnerabilities.append(vuln)
    return vuln_hosts, vulnerabilities


def parse_testssl(args):
    # test if combined_issues.csv exists
    if os.path.isfile(os.path.join(args.input_dir, "combined_issues.csv")):
        os.remove(os.path.join(args.input_dir, "combined_issues.csv"))
    issues, file_count = get_issues(args.input_dir)
    out_csv = os.path.join(args.input_dir, "combined_issues.csv")
    issue_count = len(issues)
    vuln_hosts, vulnerabilities = create_vulnerabilities(issues)
    vuln_count = len(vulnerabilities)
    output_vulns = [[
        "ID", "Finding", "Affected Device/Technology", "Risk Level", "Business Impact",
        "Remediation Procedure", "Resource Required",
    ]]
    med_vuln_count = 0
    low_vuln_count = 0
    for vuln in vulnerabilities:
        if vuln.risk_level == 'M':
            med_vuln_count += 1
        elif vuln.risk_level == 'L':
            low_vuln_count += 1
        output_vulns.append(vuln.list_format())
    out_csv = os.path.join(args.input_dir, "combined_issues.csv")
    utils.write_list_to_csv(output_vulns, out_csv)
    log.info(f"Processed {file_count} files and found {issue_count} issues. {vuln_count} of the issues were vulnerabilities.")
    log.info(f"Of the {vuln_count} vulnerabilities found:")
    log.info(f"{med_vuln_count} are considered medium risk.")
    log.info(f"{low_vuln_count} are considered low risk.")
    log.info(f"Vulnerable hosts: {vuln_hosts}")


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
