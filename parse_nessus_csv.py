#!/usr/bin/env python
"""
Parse nessus scan csv

Usage
-----
python <path to script>/parse_nessus_csv.py <input> <output>

Parameters
----------
input : string
    Required - Full path to the exported nessus scan.
output : string
    Required - Full path to the directory where the results will be written.
verbose (-v) : None
    Optional - Print debug logs to stdout
quiet (-q) : None
    Optional - Print error logs to stdout

Output
------
creates the file "nessus_parsed.csv" within the "output"


default nessus columns:
    Plugin ID, CVE, CVSS, Risk, Host, Protocol, Port, Name, Synopsis, Description, Solution, See Also, Plugin Output

result columns:
    Index, Finding, Affected Device/Technology, Risk Level, Business Impact, Remediation Procedure, Resource Required

mapping:
    Columns:
        Name -> Finding
        Host:Port (Protocol) -> Affected Device/Technology
        Risk -> Risk Level
        Description -> Business Impact
        Solution -> Remediation Procedure

    Criticality:
        Critical -> H
        High -> H
        Medium -> M
        Low -> L
"""
import os
import csv
import sys
import errno
import argparse
import logging.config

import utils
import logging_config  # noqa pylint: disable=unused-import
from models import NessusVulnerability
log = logging.getLogger("ptscripts.parse_nessus_csv")


def add_vulnerability_and_host(vulnerabilities, nessus_vuln):
    """ Check if vulnerability is already in 'vulnerabilities' if it is
    add host. if not, create vulnerability, add host and return vulnerabilities."""
    log.debug("Searching vulnerabilities for id: {}".format(nessus_vuln['Plugin ID']))
    if utils.find_vulnerability(vulnerabilities, nessus_vuln['Plugin ID']):
        log.debug("Vulnerability exists: {}".format(nessus_vuln['Plugin ID']))
        vuln = utils.find_vulnerability(vulnerabilities, nessus_vuln['Plugin ID'])
        vuln.add_affected(nessus_vuln)
        log.debug("Host added to vulnerability.")
    else:
        log.debug("Vulnerability does not exist: {}".format(nessus_vuln['Plugin ID']))
        vuln = NessusVulnerability(
            nessus_vuln['Name'], nessus_vuln['Risk'],
            nessus_vuln['Plugin ID'], nessus_vuln['Description'], nessus_vuln['Solution'])
        log.debug("Adding affected host to vulnerability: {}".format(nessus_vuln['Plugin ID']))
        vuln.add_affected(nessus_vuln)
        vulnerabilities.append(vuln)
    return vulnerabilities


def filter_vulns(vulns):
    risk_filter = ["Critical", "High", "Medium", "Low"]
    return [vuln for vuln in vulns if vuln['Risk'] in risk_filter]


def main(args):
    # verify file exists
    if not os.path.isfile(args.input):
        log.error("Couldn't find csv file at: {}".format(args.input))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.input)  # pylint: disable=undefined-variable
    log.info("Reading nessus output: {}".format(args.input))

    # read nessus file into a dict.
    nessus_dict = utils.csv_to_dict(args.input)
    found_issues = len(nessus_dict)
    log.info("Found {} issues.".format(len(nessus_dict)))

    # filter dict
    log.info("Filtering issues.")
    nessus_dict = filter_vulns(nessus_dict)
    filtered_issues = found_issues - len(nessus_dict)
    log.info("{} issues were filtered out.".format(filtered_issues))

    # Create vulnerabilities
    vulnerabilities = []
    for row in nessus_dict:
        add_vulnerability_and_host(vulnerabilities, row)

    log.info("{} vulnerabilities rated High".format(
        len([vuln for vuln in vulnerabilities if vuln.risk_level == 'H'])))
    log.info("{} vulnerabilities rated Medium".format(
        len([vuln for vuln in vulnerabilities if vuln.risk_level == 'M'])))
    log.info("{} vulnerabilities rated Low".format(
        len([vuln for vuln in vulnerabilities if vuln.risk_level == 'L'])))

    # sort vulnerabilities based on criticality
    log.info("Sorting vulnerabilities by risk.")
    sorted_vulnerabilities = utils.sort_vulnerabilities(vulnerabilities)
    log.info("Vulnerabilities sorted.")

    # format vulnerabilities
    formatted = [vuln.dict_format() for vuln in sorted_vulnerabilities]

    # write dict to csv
    fieldnames = ["index", "finding", "affected", "risk_level", "impact", "remediation", "resource"]
    header = ["Index", "Finding", "Affected Device/Technology", "Risk Level", "Business Impact",
              "Remediation Procedure", "Resource Required"]
    out_csv = os.path.join(args.output, "parsed_nessus.csv")
    log.info("Writing output.")
    with open(out_csv, "w") as f:
        dwriter = csv.DictWriter(f, fieldnames=fieldnames)
        dwriter.writer.writerow(header)
        for row in formatted:
            dwriter.writerow(row)
    log.info("Wrote the parsed output to: {}".format(out_csv))


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog='parse_nessus_csv.py',
        parents=[utils.parent_argparser()],
        description='Parse an exported nessus scan.',
    )
    parser.add_argument('input', help='Nessus CSV file.')
    parser.add_argument('output', help='Directory where the output file "parsed_nessus.csv"')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
