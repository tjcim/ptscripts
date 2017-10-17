import os
import csv
import pytest

import ptscripts.utils as utils


@pytest.fixture
def ports_dict():
    expected = [
        {"port": "22", "protocol": "tcp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "ssh", "service_tunnel": "", "product_name": "OpenSSH", "product_version": "7.2", "banner": "SSH-2.0-OpenSSH_7.2"},
        {"port": "53", "protocol": "tcp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "domain", "service_tunnel": "", "product_name": "dnsmasq", "product_version": "2.76", "banner": ""},
        {"port": "80", "protocol": "tcp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "http", "service_tunnel": "", "product_name": "nginx", "product_version": "", "banner": ""},
        {"port": "443", "protocol": "tcp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "http", "service_tunnel": "ssl", "product_name": "nginx", "product_version": "", "banner": ""},
        {"port": "3000", "protocol": "tcp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "http", "service_tunnel": "ssl", "product_name": "Mongoose httpd", "product_version": "", "banner": ""},
        {"port": "53", "protocol": "udp", "ipv4": "10.0.0.1", "mac": "00:78:2A:E8:35:29", "hostnames": "", "service_name": "domain", "service_tunnel": "", "product_name": "dnsmasq", "product_version": "2.76", "banner": ""},
        {"port": "80", "protocol": "tcp", "ipv4": "10.0.0.7", "mac": "B8:AE:ED:EC:16:23", "hostnames": "", "service_name": "http", "service_tunnel": "", "product_name": "nginx", "product_version": "1.11.10", "banner": ""},
        {"port": "2376", "protocol": "tcp", "ipv4": "10.0.0.7", "mac": "B8:AE:ED:EC:16:23", "hostnames": "", "service_name": "docker", "service_tunnel": "ssl", "product_name": "", "product_version": "", "banner": ""},
        {"port": "5000", "protocol": "tcp", "ipv4": "10.0.0.7", "mac": "B8:AE:ED:EC:16:23", "hostnames": "", "service_name": "http", "service_tunnel": "", "product_name": "Werkzeug httpd", "product_version": "0.11.11", "banner": ""},
        {"port": "5355", "protocol": "tcp", "ipv4": "10.0.0.7", "mac": "B8:AE:ED:EC:16:23", "hostnames": "", "service_name": "llmnr", "service_tunnel": "", "product_name": "", "product_version": "", "banner": ""},
        {"port": "32768", "protocol": "tcp", "ipv4": "10.0.0.7", "mac": "B8:AE:ED:EC:16:23", "hostnames": "", "service_name": "http", "service_tunnel": "", "product_name": "MochiWeb Erlang HTTP library", "product_version": "1", "banner": ""},
    ]
    return expected


@pytest.fixture
def ports_csv(ports_dict, tmpdir):  # pylint: disable=redefined-outer-name
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "output.csv")
    with open(output_file, 'w') as csvfile:
        fieldnames = [
            "port", "protocol", "ipv4", "mac", "hostnames", "service_name", "service_tunnel",
            "product_name", "product_version", "banner"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in ports_dict:
            writer.writerow(row)
    return output_file


def test_uses_encryption():
    assert utils.uses_encryption('https://www.google.com')
    assert utils.uses_encryption('http://www.google.com') is False
    assert utils.uses_encryption('https://blah.com:8443')


def test_csv_to_dict(ports_dict, ports_csv):  # pylint: disable=redefined-outer-name
    assert utils.csv_to_dict(ports_csv) == ports_dict


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
