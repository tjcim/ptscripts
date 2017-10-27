import os
import unittest

from ptscripts.utils import utils
from ptscripts.models import models


class TestVulnerabilities(unittest.TestCase):

    def setUp(self):
        self.first = models.Vulnerability(finding="first", risk_level="H", _id="foo")
        self.second = models.Vulnerability(finding="second", risk_level="M", _id="bar")
        self.third = models.Vulnerability(finding="third", risk_level="L", _id="baz")
        self.fourth = models.Vulnerability(finding="fourth", risk_level="H", _id="box")
        self.fifth = models.Vulnerability(finding="fifth", risk_level="M", _id="car")

    def tearDown(self):
        self.first = None
        self.second = None
        self.third = None
        self.fourth = None
        self.fifth = None

    def test_sort_vulnerabilities(self):
        vulnerabilities = [self.third, self.second, self.first]
        expected = [self.first, self.second, self.third]
        results = utils.sort_vulnerabilities(vulnerabilities)
        assert results == expected

    def test_find_vulnerability(self):
        vulnerabilities = [self.first, self.second, self.third, self.fourth, self.fifth]
        expected = self.third
        results = utils.find_vulnerability(vulnerabilities, "baz")
        assert expected == results

    def test_find_vulnerability_none(self):
        vulnerabilities = [self.first, self.second, self.third, self.fourth, self.fifth]
        results = utils.find_vulnerability(vulnerabilities, "barr")
        assert results is None


def test_parse_csv_for_webservers(ports_csv):
    expected = [
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '443', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'Mongoose httpd', 'protocol': 'tcp',
         'port': '3000', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '', 'hostnames': '',
         'product_version': '1.11.10', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'Werkzeug httpd', 'protocol': 'tcp',
         'port': '5000', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '', 'hostnames': '',
         'product_version': '0.11.11', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'MochiWeb Erlang HTTP library',
         'protocol': 'tcp', 'port': '32768', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '',
         'hostnames': '', 'product_version': '1.0', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:11:32:73:03:38', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '443', 'mac': '00:11:32:73:03:38', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'Werkzeug httpd', 'protocol': 'tcp',
         'port': '5075', 'mac': '00:11:32:73:03:38', 'service_tunnel': '', 'hostnames': '',
         'product_version': '0.10.4', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'Plex Media Server httpd',
         'protocol': 'tcp', 'port': '32400', 'mac': '00:11:32:73:03:38', 'service_tunnel': '',
         'hostnames': '', 'product_version': '', 'service_name': 'http'},
    ]
    results = utils.parse_csv_for_webservers(ports_csv)
    assert expected == results


class TestDirExists:  # pylint: disable=no-init
    # dir does not exist, create it
    def test_create_dir(self, tmpdir):  # pylint: disable=no-self-use
        new_dir = tmpdir.join("asdfasdf").strpath
        # Make sure it doesn't exist
        assert os.path.isdir(new_dir) is False
        # Create it
        assert utils.dir_exists(new_dir, True)
        # Make sure it was created
        assert os.path.isdir(new_dir) is True

    # dir does not exist, do not create it
    def test_does_not_exist_do_not_create_dir(self):  # pylint: disable=no-self-use
        new_dir = "/tmp/doesnotexistasdf"
        # Make sure it doesn't exist
        assert os.path.isdir(new_dir) is False
        # Run dir_exists
        assert utils.dir_exists(new_dir, False) is False
        # Make sure it was not created
        assert os.path.isdir(new_dir) is False

    # dir already exists
    def test_already_exists(self, tmpdir):  # pylint: disable=no-self-use
        new_dir = tmpdir.join("ffsdfsdfsdf").strpath
        os.mkdir(new_dir)
        assert utils.dir_exists(new_dir) is True


def test_run_command_tee_aha(tmpdir):
    html_output = tmpdir.join("command.html").strpath
    command = 'echo "hello tjcim"'
    utils.run_command_tee_aha(command, html_output)
    expected = """\
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!-- This file was created with the aha Ansi HTML Adapter. https://github.com/theZiz/aha -->
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="application/xml+xhtml; charset=UTF-8" />
<title>stdin</title>
</head>
<body style="color:white; background-color:black">
<pre>
&quot;hello tjcim&quot;
</pre>
</body>
</html>
"""
    assert os.path.isfile(html_output)
    with open(html_output, 'r') as f:
        results = f.read()
    assert expected == results


def test_uses_encryption():
    assert utils.uses_encryption('https://www.google.com')
    assert utils.uses_encryption('http://www.google.com') is False
    assert utils.uses_encryption('https://blah.com:8443')


def test_csv_to_dict(nmap_dict, ports_csv):  # pylint: disable=redefined-outer-name
    assert utils.csv_to_dict(ports_csv) == nmap_dict


def test_parse_webserver_urls(tmpdir):
    # Create webserver list
    expected_webservers = ['http://104.10.1.1', 'https://www.google.com',
                           'http://www.reddit.com:8443', 'http://192.168.3.5:10439']
    tmp_input = tmpdir.join('webservers.txt')
    with open(tmp_input.strpath, 'w') as f:
        for webserver in expected_webservers:
            f.write(webserver + '\r\n')

    # Run the parse
    webservers = utils.parse_webserver_urls(tmp_input.strpath)

    assert expected_webservers == webservers


def test_get_hosts_with_port_open(ports_csv):
    expected = [
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '', 'hostnames': '',
         'product_version': '1.11.10', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:11:32:73:03:38', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
    ]
    results = utils.get_hosts_with_port_open(ports_csv, 80)
    assert expected == results

    # Test a port that doesn't exist.
    expected = []
    results = utils.get_hosts_with_port_open(ports_csv, 25)
    assert expected == results

    # Test an invalid number
    expected = []
    results = utils.get_hosts_with_port_open(ports_csv, -1)
    assert expected == results

    # Test text as port number
    expected = []
    results = utils.get_hosts_with_port_open(ports_csv, "abc")
    assert expected == results


def test_get_ips_with_port_open(ports_csv):
    expected = ['10.0.0.1', '10.0.0.7', '10.0.0.45']
    results = utils.get_ips_with_port_open(ports_csv, 80)
    assert expected == results

    # Test a port that doesn't exist.
    expected = []
    results = utils.get_ips_with_port_open(ports_csv, 25)
    assert expected == results
