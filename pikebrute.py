"""
Pike Brute is a python version of KMGBully's (https://github.com/kmgbully) ikebrute.

This script will run ike-scan on all ips with port 500 open and look for any that are in aggressive mode.
All aggressive mode VPNs are then run through ike-scan again with each id in the wordlist.dic file and
the hashes are saved. Once ike-scan is done psk-crack is run on each of the hash files using either a
provided dictionary or the default psk-crack-dictionary if one is not provided. The output of psk-crack
is saved to a file pskbrute_results.txt file, if the psk appears to be cracked the script will save that
entry to the cracked_psks.txt file.

Parameters
----------
input : string
    Required. Path to a csv file in the same format that is provided by the nmap_to_csv.py script.
out_dir : string
    Required. Path to the folder where the output is stored.
--dictionary,d : string
    Optional. Path to a dictionary file to use. If not supplied the psk-crack-dictionary will be used.
-v : None
    Optional. The more v's provided the more verbose the script output will be. Debug is -vvv.

"""
import os
import argparse
import subprocess
import logging

import config
from utils import get_ips_with_port_open, text_file_lines_to_list, dir_exists, find_files


LOGLEVELS = {0: 'ERROR', 1: 'WARNING', 2: 'INFO', 3: 'DEBUG'}


def run_ike_scan(name, ip, output=None):
    logger = logging.getLogger('main.run_ike_scan')
    if output:
        hash_file = "{}_{}.hash".format(ip, name)
        hash_path = os.path.join(output, hash_file)
    command_text = 'ike-scan -M -A {}--id={} {}'.format(
        "--pskcrack={} ".format(hash_path) if output else "", name, ip)
    logger.info('Running command: {}'.format(command_text))
    command = command_text.split()
    cp = subprocess.run(command, stdout=subprocess.PIPE)  # pylint: disable=no-member
    return cp.stdout.decode('utf-8')


def run_pskcrack(psk_file, dictionary_path):
    logger = logging.getLogger('main.run_pskcrack')
    command_text = 'psk-crack {} --dictionary={}'.format(psk_file, dictionary_path)
    logger.info('Running command: {}'.format(command_text))
    command = command_text.split()
    cp = subprocess.run(command, stdout=subprocess.PIPE)  # pylint: disable=no-member
    return cp.stdout.decode('utf-8')


def create_logger(verbose):
    logger = logging.getLogger('main')
    logger.setLevel(LOGLEVELS[verbose])
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[{levelname}] {message}', style='{')  # pylint: disable=unexpected-keyword-arg
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def capture_hashes(ip_dir, wordlist, ip):
    """ Runs ike-scan with each name in wordlist and captures the hash. """
    logger = logging.getLogger('main.capture_hashes')
    for name in wordlist:
        results = run_ike_scan(name, ip, ip_dir)
        logger.debug(results)


def is_aggressive(ip):
    """ We run ike-scan and look for aggressive in output. We return True if aggressive."""
    logger = logging.getLogger('main.is_aggressive')
    results = run_ike_scan('test', ip)
    logger.debug('Results: {}'.format(results))
    if "Aggressive Mode" in results:
        logger.info('Aggressive mode found for ip {}'.format(ip))
        return True
    else:
        logger.info('No aggressive mode found.')


def get_ike_aggressive(ips):
    logger = logging.getLogger('main.get_ike_aggressive')
    aggressive_ips = []
    for ip in ips:
        logger.info('Checking ike aggressive mode on ip: {}'.format(ip))
        if is_aggressive(ip):
            aggressive_ips.append(ip)
    return aggressive_ips


def filter_pskcrack_output(results, ip, ip_dir, psk_file):
    """ Takes the results from run_pskcrack and filters the output to only the result line. """
    output = ""
    cracked = ""
    logger = logging.getLogger('main.filter_pskcrack_output')
    lines = results.splitlines()
    for line in lines:
        if not line.startswith(('Starting', 'Ending', 'Running')):
            if not line.startswith('no match found'):
                logger.info('PSK Cracked!: {}'.format(line))
                cracked = "Cracked psk on ip: {}. PSK file: {}, psk-crack output: {}".format(
                    ip, os.path.join(ip_dir, psk_file), line)
            output = line
    return (output, cracked)


def pikebrute_multi(args):  # pylint: disable=too-many-locals
    """ Wrapper for the pikebrute function that runs it once per ip. """
    create_logger(args.verbose)
    logger = logging.getLogger('main.pikebrute_multi')
    output = []
    cracked = []
    if args.dictionary:
        if os.path.isfile(args.dictionary):
            logger.info('Using dictionary provided in arguments here: {}'.format(args.dictionary))
            dictionary_path = args.dictionary
        else:
            logger.warn('Dictionary provided ({}) cannot be found, using the default.'.format(
                args.dictionary))
    else:
        dictionary_path = os.path.join(config.SCRIPTS_PATH, 'psk-crack-dictionary')
        logger.info('Using the default dictionary: {}'.format(dictionary_path))
    ike_ips = get_ips_with_port_open(args.input, 500)
    aggressive = get_ike_aggressive(ike_ips)
    vpn_name_list = text_file_lines_to_list(os.path.join(config.SCRIPTS_PATH, 'wordlist.dic'))
    dir_exists(args.out_dir, True)
    for ip in aggressive:
        ip_dir = os.path.join(args.out_dir, ip)
        dir_exists(ip_dir, True)
        capture_hashes(ip_dir, vpn_name_list, ip)
        # Run psk-crack
        psk_files = find_files(ip_dir, suffix='.hash')
        for psk_file in psk_files:
            logger.debug('')
            results = run_pskcrack(os.path.join(ip_dir, psk_file), dictionary_path)
            filtered_out, filtered_cracked = filter_pskcrack_output(results, ip, ip_dir, psk_file)
            if filtered_out:
                output.append(filtered_out)
            if filtered_cracked:
                cracked.append(filtered_cracked)
    results_file = os.path.join(args.out_dir, "pikebrute_results.txt")
    cracked_file = os.path.join(args.out_dir, "cracked_psks.txt")
    with open(results_file, 'w') as f:
        f.write('\r\n'.join(output))
    with open(cracked_file, 'w') as f:
        f.write('\r\n'.join(cracked))


def parse_args():
    parser = argparse.ArgumentParser(prog='pikebrute.py')
    parser.add_argument('input', help='CSV File created from nmap_to_csv.py.')
    parser.add_argument('out_dir', help='Output directory and working folder.')
    parser.add_argument(
        '--dictionary', '-d',
        help='Dictionary that psk_crack should use. If not provided the script will use the \
psk-crack-dictionary. Must be the full path to the file.')
    parser.add_argument('-v', action='count', default=0,
                        help='Verbosity of the application. Max verbosity -vvv.')
    return parser.parse_args()


if __name__ == '__main__':
    pikebrute_multi(parse_args())
