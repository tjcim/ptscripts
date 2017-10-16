"""
Run Nikto on multiple webservers

Parameters
----------
input_file : string
    Required - Full path to ports.csv file created from nmap_to_csv.py script
output_dir : string
    Required - Full path to the directory in which the nikto files will be saved.

Usage
-----
python multi_nikto.py /path/to/ports.csv /path/to/output/nikto/

"""
import os
import sys
import logging
import argparse
import subprocess

import utils
import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_nikto")
NIKTO_COMMAND = "{proxy}nikto -C all -host {ip} -port {port}{ssl} -output {output_csv_file}"


def run_nikto(webserver, output_dir, proxy):  # pylint: disable=too-many-locals
    LOG.debug("Running run_nikto for {}".format(webserver))
    ip = webserver['ip_addr']
    port = webserver['port']
    output_csv_file = os.path.join(output_dir, "Nikto_{ip}_{port}.csv".format(ip=ip, port=port))
    output_html_file = os.path.join(output_dir, "Nikto_{ip}_{port}.html".format(ip=ip, port=port))
    service_name = webserver['service_name']
    tunnel = webserver['tunnel']
    command_formatted = NIKTO_COMMAND.format(
        ip=ip, port=port, output_csv_file=output_csv_file,
        proxy='proxychains' if proxy else "",
        ssl=' -ssl' if service_name == 'https' or tunnel == 'ssl' else "",
    )
    LOG.debug("Starting nikto on {} running on port {} using the following command:".format(
        ip, port))
    LOG.debug(command_formatted)
    p1 = subprocess.Popen(command_formatted.split(), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['aha', '-b'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    LOG.debug("Writing output to {}".format(output_html_file))
    with open(output_html_file, 'wb') as h:
        h.write(output)


def run_nikto_on_webservers(args):
    """ Parse csv and then run nikto for each."""
    LOG.info("Saving output to {}".format(args.output_dir))
    utils.dir_exists(args.output_dir, True)
    LOG.info("Getting webservers from {}".format(args.input_file))
    webservers = utils.parse_csv_for_webservers(args.input_file)
    for webserver in webservers:
        run_nikto(webserver, args.output_dir, args.proxy)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run Nikto on multiple urls servers.',
        prog='multi_nikto.py',
    )
    parser.add_argument('input_file', help='CSV File of open ports.')
    parser.add_argument('output_dir', help='Output directory where nikto reports will be created.')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    run_nikto_on_webservers(parse_args(sys.argv[1:]))
