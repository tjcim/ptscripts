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
import subprocess

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_nikto")
NIKTO_COMMAND = "{proxy}nikto -C all -host {ip} -port {port}{ssl} -output {output_csv_file}"


def run_command_tee_aha(command, html_output):
    LOG.info("Starting nikto.")
    LOG.debug("Running command {}".format(command))
    try:
        process = subprocess.run(command.split(), stdout=subprocess.PIPE)
        process_stdout = str(process.stdout, 'utf-8')
        p2 = subprocess.run(['tee', '/dev/tty'], input=process.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    except subprocess.TimeoutExpired:  # pylint: disable=no-member
        LOG.warning("Timeout error occurred for url.")
        return
    if "No web server found on" in process_stdout:
        LOG.info("The remote website didn't respons.")
        return
    p3 = subprocess.run(['aha', '-b'], input=p2.stdout, stdout=subprocess.PIPE)  # pylint: disable=no-member
    output = p3.stdout
    LOG.debug("Writing output to {}".format(html_output))
    with open(html_output, 'wb') as h:
        h.write(output)


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
    nikto_folder = os.path.join(args.output_dir, "nikto")
    LOG.info("Saving output to {}".format(nikto_folder))
    utils.dir_exists(nikto_folder, True)
    LOG.info("Getting webservers from {}".format(args.input_file))
    webservers = get_webservers(args.input_file)
    for webserver in webservers:
        url = "{}://{}:{}".format(webserver['service_name'], webserver['ipv4'], webserver['port'])
        if not utils.check_url(url):
            continue
        LOG.debug("Working on url: {}:{}".format(webserver['ipv4'], webserver['port']))
        command, html_output = create_command(webserver, nikto_folder, args.proxy)
        run_command_tee_aha(command, html_output)


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
