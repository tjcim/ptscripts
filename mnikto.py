"""
Run nikto save data and create images of the results

USAGE: python mnikto.py <output_dir> --url <url>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse

from utils import utils  # noqa
from utils import logging_config  # noqa pylint: disable=unused-import
from utils import run_commands


log = logging.getLogger("ptscripts.web_nikto")
NIKTO_COMMAND = "/opt/nikto/program/nikto.pl -C all -maxtime 1h -nointeractive "\
    "-useragent 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    " Chrome/40.0.2214.85 Safari/537.36' -ask auto -o {output} -host {domain} -port {port}{root}{ssl}"
NIKTO_PROXY_COMMAND = "/opt/nikto/program/nikto.pl -C all -maxtime 1h -nointeractive "\
    "-useragent 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    " Chrome/40.0.2214.85 Safari/537.36' -ask auto -o {output} -host {domain} -port {port}{root}"\
    " -nossl -useproxy http://{proxy}/"


def run_nikto(url_dict, output_dir, proxy, screenshot=False):
    html_path = os.path.join(output_dir, f"nikto_{url_dict['domain']}_{url_dict['port']}.html")
    csv_path = os.path.join(output_dir, f"nikto_{url_dict['domain']}_{url_dict['port']}.csv")
    if proxy:
        log.info(f"Using proxy: {proxy}")
        command_text = NIKTO_PROXY_COMMAND
    else:
        command_text = NIKTO_COMMAND
    log.info(command_text)
    command = command_text.format(domain=url_dict['domain'], port=url_dict['port'],
                                  root=url_dict['root'], ssl=url_dict['ssl'], output=csv_path,
                                  proxy=proxy)
    log.info('Running command: {}'.format(command))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and screenshot:
        log.info("Creating a screenshot of the output and saving it to {}".format(screenshot))
        utils.dir_exists(screenshot, True)
        utils.selenium_image(html_output, screenshot)
    if not html_output:
        log.error("Didn't receive a response from running the command.")


def parse_url_nikto(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    # if non-standard port break it up.
    if ":" in netloc:
        domain = netloc.split(":")[0]
        port = netloc.split(":")[1]
    # otherwise port is based on scheme
    else:
        domain = netloc
        if parsed_url.scheme == 'http':
            port = '80'
        else:
            port = '443'
    if parsed_url.scheme == 'https':
        ssl = " -ssl"
    else:
        ssl = ""
    if parsed_url.path:
        root = " -root " + parsed_url.path
    else:
        root = ""
    return {'domain': domain, 'port': port, 'root': root, 'ssl': ssl}


def main(args):
    os.makedirs(args.output, exist_ok=True)
    urls = []
    # Prepare commands
    if args.csv:
        log.info('Running nikto against CSV file.')
        webservers = utils.parse_csv_for_webservers(args.csv)
        for webserver in webservers:
            if webserver['service_tunnel'] == 'ssl' or webserver['service_name'] == 'https':
                ssl = " -ssl"
            else:
                ssl = ""
            port = webserver['port']
            domain = webserver['ipv4']
            root = ""
            urls.append({'domain': domain, 'port': port, 'root': root, 'ssl': ssl})
    elif args.url:
        log.info('Running nikto against a single URL.')
        parsed_url = parse_url_nikto(args.url)
        urls.append(parsed_url)
    else:
        log.info('Running nikto against a text file of URLs.')
        with open(args.txt, 'r') as f:
            for line in f:
                parsed_url = parse_url_nikto(line.strip())
                urls.append(parsed_url)
    if args.screenshot:
        screenshot = args.screenshot
    else:
        screenshot = False
    url_count = len(urls)
    for i, url in enumerate(urls, start=1):
        log.info('**** Number {} of {} ****'.format(i, url_count))
        run_nikto(url, args.output, args.proxy, screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run nikto against one or many targets.',
    )

    # Mutually exclusive inputs: csv, url, list of sites.
    input_arg = parser.add_mutually_exclusive_group()
    input_arg.add_argument('--csv', help='CSV File of open ports.')
    input_arg.add_argument('--url', help="Single url to be tested")
    input_arg.add_argument('--txt', help='Text file with url per line.')

    parser.add_argument('output', help="where to store results")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshot will be saved.")
    parser.add_argument("-p", "--proxy", help="proxy")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Logger set to debug.")
    else:
        logger.setLevel('INFO')

    if not args.csv and not args.url and not args.txt:
        print('You must provide either a single URL (--url), a CSV file (--csv) or a text file (--txt)')
        sys.exit()
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
