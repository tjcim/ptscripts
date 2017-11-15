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
import threading
import subprocess
from queue import Queue

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.multi_nikto")
NIKTO_COMMAND = "{proxy}nikto -C all -host {ip} -port {port}{ssl} -output {output_csv_file} -ask auto -Display P -nointeractive -timeout 4 -until 59m"


def run_command_tee_aha(command, html_output):
    LOG.info("Starting nikto.")
    LOG.info("Running command {}".format(command))
    try:
        process = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=60 * 60)  # 60 minute timeout
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
    command_text = "<p style='color:#00CC00'>{}</p>".format(command)
    with open(html_output, 'wb') as h:
        h.write(command_text.encode())
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


def process_queue(webserver_queue, nikto_folder, args):
    while True:
        webserver = webserver_queue.get()
        url = "{}://{}:{}".format(webserver['service_name'], webserver['ipv4'], webserver['port'])
        if not utils.check_url(url)[0]:
            continue
        LOG.debug("Working on url: {}:{}".format(webserver['ipv4'], webserver['port']))
        command, html_output = create_command(webserver, nikto_folder, args.proxy)
        run_command_tee_aha(command, html_output)
        webserver_queue.task_done()
        continue


def main(args):
    """ Parse csv and then run nikto for each."""
    nikto_folder = os.path.join(args.output_dir, "nikto")
    LOG.info("Saving output to {}".format(nikto_folder))
    utils.dir_exists(nikto_folder, True)
    LOG.info("Getting webservers from {}".format(args.input_file))
    webservers = get_webservers(args.input_file)
    webserver_queue = Queue()

    LOG.info("Starting {} threads.".format(args.threads))
    for _ in range(args.threads):
        t = threading.Thread(
            target=process_queue,
            kwargs={
                'webserver_queue': webserver_queue,
                'nikto_folder': nikto_folder,
                'args': args,
            }
        )
        t.daemon = True
        t.start()

    for current_webserver in webservers:
        webserver_queue.put(current_webserver)

    webserver_queue.join()


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run Nikto on multiple urls servers.',
        prog='multi_nikto.py',
    )
    parser.add_argument('input_file', help='CSV File of open ports.')
    parser.add_argument('output_dir', help='Output directory where nikto reports will be created.')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    parser.add_argument('-t', '--threads', help="Number of threads (default is 2).",
                        default=2, type=int)
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
