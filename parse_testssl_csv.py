import os
import argparse

from utils import csv_to_list, write_list_to_csv


class Vulnerability:
    def __init__(self, name, criticality, _id):
        self.name = name
        self.criticality = criticality
        self.id = _id
        self.hosts = []

    def add_host(self, issue):
        ip = issue[1].split('/')[1]
        port = issue[2]
        self.hosts.append((ip, port))

    def csv_format(self):
        affected_hosts = []
        for host in self.hosts:
            affected_hosts.append("{}:{}".format(host[0], host[1]))
        formatted_hosts = ", ".join(affected_hosts)
        return [self.name, formatted_hosts, self.criticality]

    def __repr__(self):
        return "{} {} {}".format(self.name, self.hosts, self.criticality)


def find_vulnerability(vulnerabilities, vuln_id):
    """ Searches the list of Vulnerability objects and returns the first with id == vuln_id else None """
    for vuln in vulnerabilities:
        if vuln.id == vuln_id:
            return vuln
    return None


def parse_testssl_output_for_issues(csv_file):
    results = []
    output = csv_to_list(csv_file)
    for row in output:
        try:
            if row[3] not in ['INFO', 'OK', 'severity']:
                results.append(row)
        except IndexError:
            print('IndexError on row: {}'.format(row))
    return results


def find_csv_filenames(input_dir, suffix='.csv'):
    filenames = os.listdir(input_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def get_issues(csv_dir):
    """ pull all the issues from the csv files. """
    issues = []
    csv_files = find_csv_filenames(csv_dir)
    for csv_file in csv_files:
        results = parse_testssl_output_for_issues(os.path.join(csv_dir, csv_file))
        for result in results:
            issues.append(result)
    return issues


def parse_testssl(csv_dir):
    # test if combined_issues.csv exists
    if os.path.isfile(os.path.join(csv_dir, "combined_issues.csv")):
        print('Remove the combined_issues.csv file in {} before running.'.format(csv_dir))
        return
    vulnerabilities = []
    issues = get_issues(csv_dir)
    for issue in issues:
        # Check if we already have a vulnerability for this issue
        if find_vulnerability(vulnerabilities, issue[0]):
            vuln = find_vulnerability(vulnerabilities, issue[0])
            vuln.add_host(issue)
        else:
            vuln = Vulnerability(issue[4], issue[3], issue[0])
            vuln.add_host(issue)
            vulnerabilities.append(vuln)
    output_vulns = []
    for vuln in vulnerabilities:
        output_vulns.append(vuln.csv_format())
    out_csv = os.path.join(csv_dir, "combined_issues.csv")
    write_list_to_csv(output_vulns, out_csv)


def parse_args():
    parser = argparse.ArgumentParser(prog='parse_testssl_csv.py')
    parser.add_argument('input', help='Directory with testssl output.')
    return parser.parse_args()


if __name__ == '__main__':
    parse_testssl(parse_args().input)
