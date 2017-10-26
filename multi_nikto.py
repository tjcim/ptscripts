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
import logging
import argparse

import utils
import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_nikto")
NIKTO_COMMAND = "{proxy}nikto -C all -host {ip} -port {port}{ssl} -output {output_csv_file}"


def create_command(webserver, output_dir, proxy):
    ip = webserver['ipv4']
    port = webserver['port']
    csv_output = os.path.join(output_dir, "Nikto_{ip}_{port}.csv".format(ip=ip, port=port))
    html_output = os.path.join(output_dir, "Nikto_{ip}_{port}.html".format(ip=ip, port=port))
    command = NIKTO_COMMAND.format(
        ip=ip, port=port, output_csv_file=csv_output,
        proxy='proxychains ' if proxy else "",
        ssl=' -ssl' if webserver['service_name'] == 'https' or webserver['service_tunnel'] == 'ssl' else "",
    )
    return (command, html_output)


def get_webservers(ports_csv):
    return utils.parse_csv_for_webservers(ports_csv)


def main(args):
    """ Parse csv and then run nikto for each."""
    LOG.info("Saving output to {}".format(args.output_dir))
    utils.dir_exists(args.output_dir, True)
    LOG.info("Getting webservers from {}".format(args.input_file))
    webservers = get_webservers(args.input_file)
    for webserver in webservers:
        LOG.debug("Working on url: {}:{}".format(webserver['ipv4'], webserver['port']))
        command, html_output = create_command(webserver, args.output_dir, args.proxy)
        utils.run_command_tee_aha(command, html_output)


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
    import sys
    main(parse_args(sys.argv[1:]))
