"""
Parse nessus scan csv

Parameters
----------
input_file : string
    Required - Full path to the exported nessus scan.
output_dir : string
    Required - Full path to the directory where the results will be written.

Output
------
creates the file "nessus_parsed.csv" within the "output_dir"


default nessus columns:
    0          1     2    3     4     5         6     7     8         9            10        11        12
    Plugin ID, CVE, CVSS, Risk, Host, Protocol, Port, Name, Synopsis, Description, Solution, See Also, Plugin Output

result columns:
    Finding, Affected Device/Technology, Risk Level, Business Impact, Remediation Procedure, Resource Required

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
import argparse
import logging.config

import utils
import logging_config  # noqa pylint: disable=unused-import
from models import NessusVulnerability
log = logging.getLogger("ptscripts.parse_nessus_csv")


def parse_nessus_vuln(nessus_vuln):
    return {
        "_id": nessus_vuln[0],
        "finding": nessus_vuln[7],
        "risk_level": nessus_vuln[3],
        "impact": nessus_vuln[9],
        "remediation": nessus_vuln[10],
        "host": nessus_vuln[4],
    }


def add_vulnerability_and_host(vulnerabilities, nessus_vuln):
    """ Check if vulnerability is already in 'vulnerabilities' if it is
    add host.
    if not, create vulnerability, add host and return vulnerabilities."""
    parsed = parse_nessus_vuln(nessus_vuln)
    log.debug("Searching vulnerabilities for id: {}".format(parsed['_id']))
    if utils.find_vulnerability(vulnerabilities, parsed['_id']):
        log.debug("Vulnerability exists: {}".format(parsed['_id']))
        vuln = utils.find_vulnerability(vulnerabilities, parsed['_id'])
        vuln.add_affected(nessus_vuln)
        log.debug("Host added to vulnerability.")
    else:
        log.debug("Vulnerability does not exist: {}".format(parsed['_id']))
        vuln = NessusVulnerability(
            parsed['finding'], parsed['risk_level'],
            parsed['_id'], parsed['impact'], parsed['remediation'])
        log.debug("Adding affected host to vulnerability: {}".format(parsed['_id']))
        vuln.add_affected(nessus_vuln)
        vulnerabilities.append(vuln)
    return vulnerabilities


def run_parse_nessus_csv(args):
    vulnerabilities = []
    output_vulns = []
    # verify file exists
    if not utils.file_exists(args.input_file):
        log.error("Couldn't find csv file at: {}".format(args.input_file))
    # CSV to list
    log.info("Reading nessus output.")
    nessus_vulns = utils.csv_to_list(args.input_file)
    for nessus_vuln in nessus_vulns:
        if nessus_vuln[3] not in ["Critical", "High", "Medium", "Low"]:
            continue
        vulnerabilities = add_vulnerability_and_host(vulnerabilities, nessus_vuln)
    sorted_vulnerabilities = utils.sort_vulnerabilities(vulnerabilities)
    for vuln in sorted_vulnerabilities:
        output_vulns.append(vuln.list_format())
    output_vulns.insert(0, [
        "Finding", "Affected Device/Technology", "Risk Level", "Business Impact",
        "Remediation Procedure", "Resource Required"
    ])
    out_csv = os.path.join(args.output_dir, "parsed_nessus.csv")
    # Save vulns to csv file
    utils.write_list_to_csv(output_vulns, out_csv)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='parse_nessus_csv.py',
        parents=[utils.parent_argparser()],
        description='Parse an exported nessus scan.',
    )
    parser.add_argument('input_file', help='Nessus CSV file.')
    parser.add_argument('output_dir', help='Directory where the output file "parsed_nessus.csv"')
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
    run_parse_nessus_csv(parse_args())
