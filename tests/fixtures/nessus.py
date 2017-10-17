import csv

import pytest


@pytest.fixture
def parsed_nessus_dict():
    return [
        {
            'Business Impact': "The 'commonName' (CN) attribute of the SSL certificate presented for this service is for a different machine. ",
            'Finding': 'SSL Certificate with Wrong Hostname',
            'Risk Level': 'H',
            'Remediation Procedure': "The 'commonName' (CN) attribute of the SSL certificate presented for this service is for a different machine.  ",
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.45:443 (tcp)',
            'Index': ''
        },
        {
            'Business Impact': 'The remote host has IP forwarding enabled. An attacker can exploit this to route packets through the host and potentially bypass some firewalls / routers / NAC filtering.  \nUnless the remote host is a router, it is recommended that you disable IP forwarding. ',
            'Finding': 'IP Forwarding Enabled',
            'Risk Level': 'H',
            'Remediation Procedure': 'The remote host has IP forwarding enabled. An attacker can exploit this to route packets through the host and potentially bypass some firewalls / routers / NAC filtering.   Unless the remote host is a router, it is recommended that you disable IP forwarding.  ',
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.45:0 (tcp)',
            'Index': ''
        },
        {
            'Business Impact': 'The X.509 certificate chain for this service is not signed by a recognized certificate authority.  If the remote host is a public host in production, this nullifies the use of SSL as anyone could establish a man-in-the-middle attack against the remote host.  \nNote that this plugin does not check for certificate chains that end in a certificate that is not self-signed, but is signed by an unrecognized certificate authority. ',
            'Finding': 'SSL Self-Signed Certificate',
            'Risk Level': 'M',
            'Remediation Procedure': 'The X.509 certificate chain for this service is not signed by a recognized certificate authority.  If the remote host is a public host in production, this nullifies the use of SSL as anyone could establish a man-in-the-middle attack against the remote host.   Note that this plugin does not check for certificate chains that end in a certificate that is not self-signed, but is signed by an unrecognized certificate authority.  ',
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.20:8443 (tcp)',
            'Index': ''
        },
        {
            'Business Impact': 'This plugin checks expiry dates of certificates associated with SSL- enabled services on the target and reports whether any have already expired. ',
            'Finding': 'SSL Certificate Expiry',
            'Risk Level': 'M',
            'Remediation Procedure': 'This plugin checks expiry dates of certificates associated with SSL- enabled services on the target and reports whether any have already expired.  ',
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.21:443 (tcp)',
            'Index': ''
        },
        {
            'Business Impact': 'This script contacts the remote DHCP server (if any) and attempts to retrieve information about the network layout.  \nSome DHCP servers provide sensitive information such as the NIS domain name, or network layout information such as the list of the network web servers, and so on.  \nIt does not demonstrate any vulnerability, but a local attacker may use DHCP to become intimately familiar with the associated network. ',
            'Finding': 'DHCP Server Detection',
            'Risk Level': 'L',
            'Remediation Procedure': 'This script contacts the remote DHCP server (if any) and attempts to retrieve information about the network layout.   Some DHCP servers provide sensitive information such as the NIS domain name, or network layout information such as the list of the network web servers, and so on.   It does not demonstrate any vulnerability, but a local attacker may use DHCP to become intimately familiar with the associated network.  ',
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.1:67 (udp)',
            'Index': ''
        },
        {
            'Business Impact': 'The remote host supports the use of RC4 in one or more cipher suites. The RC4 cipher is flawed in its generation of a pseudo-random stream of bytes so that a wide variety of small biases are introduced into the stream, decreasing its randomness. \nIf plaintext is repeatedly encrypted (e.g., HTTP cookies), and an attacker is able to obtain many (i.e., tens of millions) ciphertexts, the attacker may be able to derive the plaintext. ',
            'Finding': 'SSL RC4 Cipher Suites Supported (Bar Mitzvah)',
            'Risk Level': 'L',
            'Remediation Procedure': 'The remote host supports the use of RC4 in one or more cipher suites. The RC4 cipher is flawed in its generation of a pseudo-random stream of bytes so that a wide variety of small biases are introduced into the stream, decreasing its randomness.  If plaintext is repeatedly encrypted (e.g., HTTP cookies), and an attacker is able to obtain many (i.e., tens of millions) ciphertexts, the attacker may be able to derive the plaintext.  ',
            'Resource Required': '',
            'Affected Device/Technology': '10.0.0.1:3000 (tcp)', 'Index': ''
        }]


@pytest.fixture
def parsed_nessus_csv(tmpdir, parsed_nessus_dict):  # pylint: disable=redefined-outer-name
    nessus_csv_file = tmpdir.join("test_parsed_nessus.csv")
    # Write dict to csv
    header = [
        "Index", "Finding", "Affected Device/Technology", "Risk Level", "Business Impact",
        "Remediation Procedure", "Resource Required"
    ]
    with open(nessus_csv_file.strpath, "w", newline='') as f:
        csvwriter = csv.DictWriter(f, fieldnames=header)
        csvwriter.writeheader()
        for row in parsed_nessus_dict:
            csvwriter.writerow(row)
    return nessus_csv_file.strpath


@pytest.fixture
def nessus_in_csv(tmpdir, nessus_in_dict):  # pylint: disable=redefined-outer-name
    nessus_csv_file = tmpdir.join("nessus_input.csv")
    # Write dict to csv
    header = [
        "Plugin ID", "CVE", "CVSS", "Risk", "Host", "Protocol", "Port", "Name", "Synopsis",
        "Description", "Solution", "See Also", "Plugin Output"
    ]
    with open(nessus_csv_file.strpath, "w", newline='') as f:
        csvwriter = csv.DictWriter(f, fieldnames=header)
        csvwriter.writeheader()
        for row in nessus_in_dict:
            csvwriter.writerow(row)
    return nessus_csv_file.strpath


@pytest.fixture
def nessus_in_dict():
    return [
        {
            'CVSS': '3.3',
            'Name': 'DHCP Server Detection',
            'CVE': '',
            'Synopsis': 'The remote DHCP server may expose information about the associated\nnetwork.',
            'Port': '67',
            'Host': '10.0.0.1',
            'Protocol': 'udp',
            'Plugin ID': '10663',
            'Solution': 'Apply filtering to keep this information off the network and remove\nany options that are not in use.',
            'Risk': 'Low',
            'See Also': '',
            'Description': 'This script contacts the remote DHCP server (if any) and attempts to\nretrieve information about the network layout. \n\nSome DHCP servers provide sensitive information such as the NIS domain\nname, or network layout information such as the list of the network\nweb servers, and so on. \n\nIt does not demonstrate any vulnerability, but a local attacker may\nuse DHCP to become intimately familiar with the associated network.',
            'Plugin Output': '\nNessus gathered the following information from the remote DHCP server :\n\n  Master DHCP server of this network : 0.0.0.0\n  IP address the DHCP server would attribute us : 10.0.0.29\n  DHCP server(s) identifier : 10.0.0.1\n  Netmask : 255.255.255.0\n  Router : 10.0.0.1\n  Domain name server(s) : 10.0.0.1\n  Host name : \n  Domain name : \n\n'
        },
        {
            'CVSS': '2.6',
            'Name': 'SSL RC4 Cipher Suites Supported (Bar Mitzvah)',
            'CVE': 'CVE-2013-2566',
            'Synopsis': 'The remote service supports the use of the RC4 cipher.',
            'Port': '3000',
            'Host': '10.0.0.1',
            'Protocol': 'tcp',
            'Plugin ID': '65821',
            'Solution': 'Reconfigure the affected application, if possible, to avoid use of RC4\nciphers. Consider using TLS 1.2 with AES-GCM suites subject to browser\nand web server support.',
            'Risk': 'Low',
            'See Also': 'http://www.nessus.org/u?217a3666\nhttp://cr.yp.to/talks/2013.03.12/slides.pdf\nhttp://www.isg.rhul.ac.uk/tls/\nhttp://www.imperva.com/docs/HII_Attacking_SSL_when_using_RC4.pdf',
            'Description': 'The remote host supports the use of RC4 in one or more cipher suites.\nThe RC4 cipher is flawed in its generation of a pseudo-random stream\nof bytes so that a wide variety of small biases are introduced into\nthe stream, decreasing its randomness.\n\nIf plaintext is repeatedly encrypted (e.g., HTTP cookies), and an\nattacker is able to obtain many (i.e., tens of millions) ciphertexts,\nthe attacker may be able to derive the plaintext.',
            'Plugin Output': '\nList of RC4 cipher suites supported by the remote server:\n\n  High Strength Ciphers (>= 112-bit key)\n\n    RC4-MD5                      Kx=RSA         Au=RSA      Enc=RC4(128)             Mac=MD5    \n    RC4-SHA Kx=RSA         Au=RSA      Enc=RC4(128)             Mac=SHA1   \n\nThe fields above are :\n\n  {OpenSSL ciphername}\n  Kx={key exchange}\n  Au={authentication}\n  Enc={symmetric encryption method}\n  Mac={message authentication code}\n  {export flag}\n'
        },
        {
            'CVSS': '6.4',
            'Name': 'SSL Self-Signed Certificate',
            'CVE': '',
            'Synopsis': 'The SSL certificate chain for this service ends in an unrecognized\nself-signed certificate.',
            'Port': '8443',
            'Host': '10.0.0.20',
            'Protocol': 'tcp',
            'Plugin ID': '57582',
            'Solution': 'Purchase or generate a proper certificate for this service.',
            'Risk': 'Medium',
            'See Also': '',
            'Description': 'The X.509 certificate chain for this service is not signed by a\nrecognized certificate authority.  If the remote host is a public host\nin production, this nullifies the use of SSL as anyone could establish\na man-in-the-middle attack against the remote host. \n\nNote that this plugin does not check for certificate chains that end\nin a certificate that is not self-signed, but is signed by an\nunrecognized certificate authority.',
            'Plugin Output': '\nThe following certificate was found at the top of the certificate\nchain sent by the remote host, but is self-signed and was not\nfound in the list of known certificate authorities :\n\n|-Subject : C=US/ST=CA/L=San Jose/O=ubnt.com/OU=UniFi/CN=UniFi\n'
        },
        {
            'CVSS': '5',
            'Name':
            'SSL Certificate Expiry',
            'CVE': '',
            'Synopsis': "The remote server's SSL certificate has already expired.",
            'Port': '443',
            'Host': '10.0.0.21',
            'Protocol': 'tcp',
            'Plugin ID': '15901',
            'Solution': 'Purchase or generate a new SSL certificate to replace the existing\none.',
            'Risk': 'Medium',
            'See Also': '',
            'Description': 'This plugin checks expiry dates of certificates associated with SSL-\nenabled services on the target and reports whether any have already\nexpired.',
            'Plugin Output': '\nThe SSL certificate has already expired :\n\n  Subject          : C=US, L=Palo Alto, OU=VMware, CN=VMware, emailAddress=none@vmware.com\n  Issuer           : C=US, L=Palo Alto, OU=VMware, CN=VMware, emailAddress=none@vmware.com\n  Not valid before : Jul 20 11:09:29 2016 GMT\n  Not valid after  : Jul 20 11:09:29 2017 GMT\n'
        },
        {
            'CVSS': '5',
            'Name': 'SSL Certificate with Wrong Hostname',
            'CVE': '',
            'Synopsis': 'The SSL certificate for this service is for a different host.',
            'Port': '443',
            'Host': '10.0.0.45',
            'Protocol': 'tcp',
            'Plugin ID': '45411',
            'Solution': 'Purchase or generate a proper certificate for this service.',
            'Risk': 'High',
            'See Also': '',
            'Description': "The 'commonName' (CN) attribute of the SSL certificate presented for\nthis service is for a different machine.",
            'Plugin Output': '\nThe identities known by Nessus are :\n\n  10.0.0.45\n  172.17.0.1\n  nas\n\nThe Common Name in the certificate is :\n\n  synology.com\n'
        },
        {
            'CVSS': '5.8',
            'Name': 'IP Forwarding Enabled',
            'CVE': 'CVE-1999-0511',
            'Synopsis': 'The remote host has IP forwarding enabled.',
            'Port': '0',
            'Host': '10.0.0.45',
            'Protocol': 'tcp',
            'Plugin ID': '50686',
            'Solution': "On Linux, you can disable IP forwarding by doing :\n\necho 0 > /proc/sys/net/ipv4/ip_forward\n\nOn Windows, set the key 'IPEnableRouter' to 0 under\n\nHKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\Tcpip\\Parameters\n\nOn Mac OS X, you can disable IP forwarding by executing the command :\n\nsysctl -w net.inet.ip.forwarding=0\n\nFor other systems, check with your vendor.",
            'Risk': 'High',
            'See Also': '',
            'Description': 'The remote host has IP forwarding enabled. An attacker can exploit\nthis to route packets through the host and potentially bypass some\nfirewalls / routers / NAC filtering. \n\nUnless the remote host is a router, it is recommended that you disable\nIP forwarding.', 'Plugin Output': ''
        },
        {
            'CVSS': '',
            'Name': 'TCP/IP Timestamps Supported',
            'CVE': '',
            'Synopsis': 'The remote service implements TCP timestamps.',
            'Port': '0',
            'Host': '10.0.0.1',
            'Protocol': 'tcp',
            'Plugin ID': '25220',
            'Solution': 'n/a',
            'Risk': 'None',
            'See Also': 'http://www.ietf.org/rfc/rfc1323.txt',
            'Description': 'The remote host implements TCP timestamps, as defined by RFC1323.  A\nside effect of this feature is that the uptime of the remote host can\nsometimes be computed.',
            'Plugin Output': ''
        },
        {
            'CVSS': '',
            'Name': 'Device Type',
            'CVE': '',
            'Synopsis': 'It is possible to guess the remote device type.',
            'Port': '0',
            'Host': '10.0.0.1',
            'Protocol': 'tcp',
            'Plugin ID': '54615',
            'Solution': 'n/a',
            'Risk': 'None',
            'See Also': '',
            'Description': 'Based on the remote operating system, it is possible to determine\nwhat the remote system type is (eg: a printer, router, general-purpose\ncomputer, etc).',
            'Plugin Output': 'Remote device type : general-purpose\nConfidence level : 65\n'
        },
        {
            'CVSS': '',
            'Name': 'SSL / TLS Versions Supported',
            'CVE': '',
            'Synopsis': 'The remote service encrypts communications.',
            'Port': '443',
            'Host': '10.0.0.1',
            'Protocol': 'tcp',
            'Plugin ID': '56984',
            'Solution': 'n/a',
            'Risk': 'None',
            'See Also': '',
            'Description': 'This plugin detects which SSL and TLS versions are supported by the\nremote service for encrypting communications.',
            'Plugin Output': '\nThis port supports TLSv1.1/TLSv1.2.\n'
        }
    ]
