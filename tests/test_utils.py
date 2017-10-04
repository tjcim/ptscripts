import pytest

import ptscripts.utils as utils


@pytest.fixture
def ports_file(tmpdir):
    # Create csv file
    csv_file = tmpdir.join('ports.csv').strpath
    test_data = """10.10.2.1,123,ntp,None,udp
10.10.2.5,80,tcpwrapped,None,tcp
10.10.2.5,139,tcpwrapped,None,tcp
10.10.2.5,443,tcpwrapped,None,tcp
10.10.2.5,445,tcpwrapped,None,tcp
10.10.2.5,515,tcpwrapped,None,tcp
10.10.2.5,631,tcpwrapped,None,tcp
10.10.2.5,3910,prnrequest,None,tcp
10.10.2.5,3911,prnstatus,None,tcp
10.10.2.5,6839,tcpwrapped,None,tcp
10.10.2.5,7435,tcpwrapped,None,tcp
10.10.2.5,8080,tcpwrapped,None,tcp
10.10.2.5,9100,jetdirect,None,tcp
10.10.2.5,9220,tcpwrapped,None,tcp
10.10.2.5,137,netbios-ns,None,udp
10.10.2.5,161,snmp,None,udp
10.10.2.5,5353,mdns,None,udp
10.10.2.6,21,ftp,None,tcp
10.10.2.6,80,http,None,tcp
10.10.2.6,443,http,ssl,tcp
10.10.2.6,515,printer,None,tcp
10.10.2.6,631,ipp,None,tcp"""
    with open(csv_file, 'w') as f:
        f.write(test_data)
    return csv_file


def test_uses_encryption():
    assert utils.uses_encryption('https://www.google.com')
    assert utils.uses_encryption('http://www.google.com') is False
    assert utils.uses_encryption('https://blah.com:8443')


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


def test_parse_csv_for_webservers(ports_file):  # pylint: disable=redefined-outer-name
    results = utils.parse_csv_for_webservers(ports_file)
    expected = [
        {'ip_addr': '10.10.2.6', 'port': '80', 'service_name': 'http', 'tunnel': 'None'},
        {'ip_addr': '10.10.2.6', 'port': '443', 'service_name': 'http', 'tunnel': 'ssl'},
    ]
    assert results == expected


def test_get_ips_with_port_open(ports_file):  # pylint: disable=redefined-outer-name
    expected_port_80 = ['10.10.2.5', '10.10.2.6']
    results_80 = utils.get_ips_with_port_open(ports_file, 80)
    assert expected_port_80 == results_80

    expected_port_445 = ['10.10.2.5']
    results_445 = utils.get_ips_with_port_open(ports_file, 445)
    assert expected_port_445 == results_445
