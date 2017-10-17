import csv
import pytest


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
