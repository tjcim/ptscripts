import os
import argparse
import subprocess

from utils import parse_csv_for_webservers, dir_exists


def run_nikto(webserver, output_dir, proxy):
    ip = webserver['ip_addr']
    port = webserver['port']
    service_name = webserver['service_name']
    tunnel = webserver['tunnel']
    print("\r\nStarting nikto on {} running on port {} using the following command:".format(
        ip, port))
    results_file = os.path.join(output_dir, "Nikto_{}_{}.html".format(ip, port))
    if proxy:
        nikto_command = 'proxychains nikto -host {} -port {} -output {}'.format(
            ip, port, results_file)
    else:
        nikto_command = 'nikto -host {} -port {} -output {}'.format(
            ip, port, results_file)
    if service_name == 'https' or tunnel == 'ssl':
        nikto_command += ' -ssl'
    print(nikto_command)
    try:
        subprocess.call(nikto_command, shell=True)
    except KeyboardInterrupt:
        return


def run_nikto_on_webservers(csv_input, output_dir, proxy):
    """ Parse csv and then run nikto for each."""
    dir_exists(output_dir, True)
    webservers = parse_csv_for_webservers(csv_input)
    for webserver in webservers:
        run_nikto(webserver, output_dir, proxy)


def parse_args():
    parser = argparse.ArgumentParser(prog='multi_nikto.py')
    parser.add_argument('input', help='CSV File of open ports.')
    parser.add_argument('output', help='Output directory where nikto reports will be created.')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    run_nikto_on_webservers(parse_args().input, parse_args().output, parse_args().proxy)
