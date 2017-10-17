import os
import xml.etree.ElementTree as ET

from ptscripts import nmap_to_csv as ntc
from ptscripts.tests.test_utilities import two_files_contain_same_info


# Unit Tests
def test_get_ipv4(xml_host):  # pylint: disable=redefined-outer-name
    ip = ntc.get_ipv4(xml_host)
    assert ip == "10.0.0.1"


def test_get_mac(xml_host):  # pylint: disable=redefined-outer-name
    mac = ntc.get_mac(xml_host)
    assert mac == "00:78:2A:E8:35:29"


def test_get_hostnames(xml_host):  # pylint: disable=redefined-outer-name
    # single hostname
    hostnames = ntc.get_hostnames(xml_host)
    assert hostnames == ["100.119.152.33.bigleaf.net"]

    # multiple hostnames
    ET.SubElement(xml_host.find('hostnames'), 'hostname', {"name": "test.host.name", "type": "PTR"})
    assert ntc.get_hostnames(xml_host) == ["100.119.152.33.bigleaf.net", "test.host.name"]


def test_get_all_ports(xml_host, xml_ports):  # pylint: disable=redefined-outer-name
    ports = ntc.get_all_ports(xml_host)
    assert len(ports) == len(xml_ports)


def test_get_protocol(xml_port):  # pylint: disable=redefined-outer-name
    protocol = ntc.get_protocol(xml_port)
    assert protocol == "tcp"


def test_get_port(xml_port):  # pylint: disable=redefined-outer-name
    port = ntc.get_port(xml_port)
    assert port == "22"


def test_is_open(xml_port):  # pylint: disable=redefined-outer-name
    # open
    assert ntc.is_open(xml_port)

    # closed
    xml_port.find('state').set('state', 'filtered')
    assert ntc.is_open(xml_port) is False


def test_get_service_name(xml_port):  # pylint: disable=redefined-outer-name
    service_name = ntc.get_service_name(xml_port)
    assert service_name == "ssh"


def test_get_service_tunnel(xml_ports):  # pylint: disable=redefined-outer-name
    # tunnel
    tunnel = ntc.get_service_tunnel(xml_ports[3])
    assert tunnel == "ssl"

    # no tunnel
    tunnel = ntc.get_service_tunnel(xml_ports[2])
    assert tunnel is None


def test_get_product(xml_port):  # pylint: disable=redefined-outer-name
    product = ntc.get_product(xml_port)
    assert product == "OpenSSH"


def test_get_version(xml_port):  # pylint: disable=redefined-outer-name
    version = ntc.get_version(xml_port)
    assert version == "7.2"


def test_get_banner(xml_port):  # pylint: disable=redefined-outer-name
    assert ntc.get_banner(xml_port) == "SSH-2.0-OpenSSH_7.2"

    # no banner
    xml_port.remove(xml_port.find('./script/[@id="banner"]'))
    assert ntc.get_banner(xml_port) is None


# Functional Test
def test_nmap_to_csv(ports_csv, tmpdir, nmap_xml):
    # args
    input_file = nmap_xml.strpath
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "ports.csv")
    args = ntc.parse_args([input_file, output_dir])

    # Run script
    ntc.parse_nmap(args)

    # compare with expected
    assert two_files_contain_same_info(output_file, ports_csv)
