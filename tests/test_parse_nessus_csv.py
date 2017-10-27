import os
import unittest

import pytest

from ptscripts.models import models
from ptscripts.parsing import parse_nessus_csv as pnc
from ptscripts.tests.test_utilities import two_csvs_contain_same_info


def test_main_csv_file_not_found(tmpdir):
    # args
    output_dir = tmpdir.strpath
    args = pnc.parse_args(["/tmp/blahblahblah.csv", output_dir])
    with pytest.raises(FileNotFoundError):  # pylint: disable=undefined-variable
        pnc.main(args)


def test_filter_vulns():
    vulns = [
        {'CVSS': '3.3', 'Name': 'DHCP Server Detection', 'CVE': '', 'Synopsis': 'The', 'Port': '67', 'Host': '10.0.0.1', 'Protocol': 'udp', 'Plugin ID': '10663', 'Solution': 'Apply.', 'Risk': 'Low', 'See Also': '', 'Description': 'This', 'Plugin Output': 'Nessus'},
        {'CVSS': '2.6', 'Name': 'SSL RC4 Cipher Suites Supported (Bar Mitzvah)', 'CVE': 'CVE-2013-2566', 'Synopsis': 'The remote service supports the use of the RC4 cipher.', 'Port': '3000', 'Host': '10.0.0.1', 'Protocol': 'tcp', 'Plugin ID': '65821', 'Solution': 'Reconfigure', 'Risk': 'Info', 'See Also': '', 'Description': 'The', 'Plugin Output': 'List'},
        {'CVSS': '6.4', 'Name': 'SSL', 'CVE': '', 'Synopsis': 'The', 'Port': '8443', 'Host': '10.0.0.20', 'Protocol': 'tcp', 'Plugin ID': '57582', 'Solution': 'Purchase', 'Risk': 'None', 'See Also': '', 'Description': 'The X.509', 'Plugin Output': 'The'},
    ]
    expected = [
        {'CVSS': '3.3', 'Name': 'DHCP Server Detection', 'CVE': '', 'Synopsis': 'The', 'Port': '67', 'Host': '10.0.0.1', 'Protocol': 'udp', 'Plugin ID': '10663', 'Solution': 'Apply.', 'Risk': 'Low', 'See Also': '', 'Description': 'This', 'Plugin Output': 'Nessus'},
    ]
    results = pnc.filter_vulns(vulns)
    assert results == expected


class TestAddVulnerabilityAndHost(unittest.TestCase):

    def setUp(self):
        self.vulnerabilities = [
            models.NessusVulnerability(finding="first", risk_level="High", _id="foo"),
            models.NessusVulnerability(finding="second", risk_level="Medium", _id="bar"),
            models.NessusVulnerability(finding="third", risk_level="Low", _id="baz"),
            models.NessusVulnerability(finding="fourth", risk_level="High", _id="box"),
            models.NessusVulnerability(finding="fifth", risk_level="Medium", _id="car"),
        ]
        self.nessus_vuln = {
            'CVSS': '3.3', 'Name': 'DHCP Server Detection', 'CVE': '', 'Synopsis': 'The',
            'Port': '67', 'Host': '10.0.0.1', 'Protocol': 'udp', 'Plugin ID': '10663',
            'Solution': 'Apply.', 'Risk': 'Low', 'See Also': '', 'Description': 'This',
            'Plugin Output': 'Nessus'
        }

    def tearDown(self):
        self.vulnerabilities = None

    def test_vulnerability_exists(self):
        self.nessus_vuln['Plugin ID'] = 'foo'
        expected = ["10.0.0.1:67 (udp)"]
        vulns = pnc.add_vulnerability_and_host(self.vulnerabilities, self.nessus_vuln)
        assert vulns[0].affected == expected

    def test_vulnerability_does_not_exist(self):
        assert len(self.vulnerabilities) == 5
        pnc.add_vulnerability_and_host(self.vulnerabilities, self.nessus_vuln)
        assert len(self.vulnerabilities) == 6


# Functional test
def test_run_parse_nessus_csv(nessus_in_csv, parsed_nessus_csv, tmpdir):
    # args
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "parsed_nessus.csv")
    args = pnc.parse_args([nessus_in_csv, output_dir])

    # Run script
    pnc.main(args)

    # Compare output
    assert two_csvs_contain_same_info(output_file, parsed_nessus_csv)
