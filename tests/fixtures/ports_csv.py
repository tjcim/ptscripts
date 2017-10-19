import csv
import pytest


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
def ports_csv(nmap_dict, tmpdir):
    ports_csv_file = tmpdir.join("test_ports.csv")
    # Write dict to csv
    header = [
        "port", "protocol", "ipv4", "mac", "hostnames", "service_name",
        "service_tunnel", "product_name", "product_version", "banner",
    ]
    with open(ports_csv_file.strpath, "w", newline='') as f:
        csvwriter = csv.DictWriter(f, fieldnames=header)
        csvwriter.writeheader()
        for row in nmap_dict:
            csvwriter.writerow(row)
    return ports_csv_file.strpath
