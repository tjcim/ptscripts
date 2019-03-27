"""
Run whatweb save data and create images of the results

USAGE: python mwhatweb.py <output_dir> --url <url>|--csv <csv>|--txt <txt> [-s <screenshot directory>]
"""
import os
import logging
import argparse
from urllib.parse import urlparse  # pylint: disable=no-name-in-module,import-error

from utils import utils
from utils import run_commands


LOG = logging.getLogger("ptscripts.mwhatweb")
WHATWEB_COMMAND = "whatweb -v -a 3 {url}"


def run_whatweb(url, output_dir, screenshot=False):
    parsed_url = urlparse(url)
    port = parsed_url.port
    if not port:
        if parsed_url.scheme == 'http':
            port = '80'
        else:
            port = '443'
    html_path = os.path.join(output_dir, f"whatweb_{parsed_url.netloc}_{port}.html")
    command = WHATWEB_COMMAND.format(url=url)
    LOG.info('Running command: {}'.format(command))
    text_output = run_commands.bash_command(command)
    html_output = run_commands.create_html_file(text_output, command, html_path)
    if html_output and screenshot:
        LOG.info("Creating a screenshot of the output and saving it to {}".format(screenshot))
        utils.dir_exists(screenshot, True)
        utils.selenium_image(html_output, screenshot)
    if not html_output:
        LOG.error("Didn't receive a response from running the command.")


def main(args):
    urls = []
    # Prepare commands
    if args.csv:
        LOG.info('Running wpscan against CSV file.')
        webservers = utils.parse_csv_for_webservers(args.csv)
        for webserver in webservers:
            if webserver['service_tunnel'] == 'ssl' or webserver['service_name'] == 'https':
                scheme = 'https://'
            else:
                scheme = 'http://'
            port = webserver['port']
            url = f'{scheme}{webserver["ipv4"]}'
            if not webserver['port'] == '80' and not webserver['port'] == '443':
                url = url + f':{port}'
            urls.append(url)
    elif args.url:
        LOG.info('Running wpscan against a single URL.')
        urls.append(args.url)
    else:
        LOG.info('Running wpscan against a text file of URLs.')
        with open(args.txt, 'r') as f:
            for line in f:
                urls.append(line.strip())
    if args.screenshot:
        screenshot = args.screenshot
    else:
        screenshot = False
    url_count = len(urls)
    for i, url in enumerate(urls, start=1):
        LOG.info('**** Number {} of {} ****'.format(i, url_count))
        run_whatweb(url, args.output, screenshot)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run whatweb against one or many targets.',
    )

    # Mutually exclusive inputs: csv, url, list of sites.
    input_arg = parser.add_mutually_exclusive_group()
    input_arg.add_argument('--csv', help='CSV File of open ports.')
    input_arg.add_argument('--url', help="Single url to be tested")
    input_arg.add_argument('--txt', help='Text file with url per line.')

    parser.add_argument('output', help="where to store results")
    parser.add_argument("-s", "--screenshot",
                        help="full path to where the screenshot will be saved.")
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


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
