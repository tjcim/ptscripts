import os
import csv
import argparse

import utils


def write_nmap_results_csv(output_file, hosts):
    """ Write the parsed hosts to the csv file. """
    header = ["Host", "Port", "Protocol", "Name", "Information"]
    with open(output_file, "w", newline='') as f:
        csvwriter = csv.writer(f)
        # Write header
        csvwriter.writerow(header)
        # Write results
        for host in hosts:
            csvwriter.writerow([
                host["ipv4"], host["port"], host["protocol"],
                host["service_name"], host["product_name"]
            ])


def main(args):
    results = utils.csv_to_dict(args.input_file)
    output_file = os.path.join(args.output, "ports_report.csv")
    write_nmap_results_csv(output_file, results)


def parse_args(args):
    parser = argparse.ArgumentParser(prog='ports_to_report.py')
    parser.add_argument('input_file', help='Ports csv file to parse.')
    parser.add_argument('output', help='Output directory where file will be created.')
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
