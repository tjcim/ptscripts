import os
import shutil
import argparse
import logging

from config import config
from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.folder_structure")


def recon_ng_rc_files(pentest_dir, domain):
    pentest_name = os.path.split(pentest_dir)[1]
    if pentest_name is None:
        pentest_name = os.path.split(os.path.split(pentest_dir)[0])[1]

    # bing_domain_web
    rc_folder = os.path.join(pentest_dir, "ept/rc_files")
    os.makedirs(rc_folder, exist_ok=True)
    LOG.info("Creating the recon_bing.rc file in {}".format(rc_folder))
    recon_bing_path = os.path.join(rc_folder, "recon_bing.rc")
    with open(recon_bing_path, "w") as f:
        f.write("workspaces delete {}\n".format(pentest_name))
        f.write("set VERBOSITY 1\n")
        f.write("workspaces add {}\n".format(pentest_name))
        f.write("add domains {}\n".format(domain))
        f.write("keys add ipinfodb_api {}\n".format(config.IPINFODB_API))
        f.write("keys add builtwith_api {}\n".format(config.BUILTWITH_API))
        f.write("show domains\n")
        f.write("use recon/domains-hosts/bing_domain_web\n")
        f.write("run\n")
        f.write("show hosts\n")
        f.write("exit\n")

    # google_site_web
    LOG.info("Creating the recon_google.rc file in {}".format(rc_folder))
    recon_google_path = os.path.join(rc_folder, "recon_google.rc")
    with open(recon_google_path, "w") as f:
        f.write("workspaces select {}\n".format(pentest_name))
        f.write("show domains\n")
        f.write("use recon/domains-hosts/google_site_web\n")
        f.write("run\n")
        f.write("show hosts\n")
        f.write("exit\n")

    # brute_hosts
    LOG.info("Creating the recon_brute.rc file in {}".format(rc_folder))
    recon_brute_path = os.path.join(rc_folder, "recon_brute.rc")
    with open(recon_brute_path, "w") as f:
        f.write("workspaces select {}\n".format(pentest_name))
        f.write("show domains\n")
        f.write("use recon/domains-hosts/brute_hosts\n")
        f.write("run\n")
        f.write("show hosts\n")
        f.write("exit\n")


def metasploit_rc_files(pentest_dir):
    pentest_name = os.path.split(pentest_dir)[1]
    if pentest_name is None:
        pentest_name = os.path.split(os.path.split(pentest_dir)[0])[1]
    # metasploit workspace and import nmap
    rc_folder = os.path.join(pentest_dir, "ept/rc_files")
    os.makedirs(rc_folder, exist_ok=True)
    LOG.info("Creating the db_import.rc file in {}".format(rc_folder))
    workspace_import_path = os.path.join(rc_folder, "db_import.rc")
    nmap_xml = os.path.join(pentest_dir, "ept/nmap/ss_all.xml")
    with open(workspace_import_path, "w") as f:
        f.write("workspace -a {}\n".format(pentest_name))
        f.write("db_import {}\n".format(nmap_xml))
        f.write("hosts")

    # endpointmapper
    LOG.info("Creating the endpoint_mapper.rc file in {}".format(rc_folder))
    endpoint_resource_file = os.path.join(rc_folder, "endpoint_mapper.rc")
    with open(endpoint_resource_file, "w") as f:
        f.write("use auxiliary/scanner/dcerpc/endpoint_mapper\n")
        f.write("hosts -R\n")
        f.write("set THREADS 10\n")
        f.write("show options\n")
        f.write("exploit")

    # smtp_relay
    LOG.info("Creating the smtp_relay.rc file in {}".format(rc_folder))
    smtp_resource_path = os.path.join(rc_folder, "smtp_relay.rc")
    with open(smtp_resource_path, "w") as f:
        f.write("use auxiliary/scanner/smtp/smtp_relay\n")
        f.write("services -p 25 -R\n")
        f.write("show options\n")
        f.write("exploit")


def checklist(pentest_dir):
    src = os.path.join(config.SCRIPTS_PATH, "templates/checklist.txt")
    dst = os.path.join(pentest_dir, "ept/checklist.txt")
    LOG.info("Writing checklist file to: {}".format(dst))
    shutil.copyfile(src, dst)


def main(args):
    base_dirs = ["ept"]
    pt_dirs = ["testssl", "whatweb", "rc_files", "nmap", "screenshots"]
    LOG.info("Creating directories")
    for directory in base_dirs:
        dir_path = os.path.join(args.input, directory)
        LOG.debug("Creating directory: {}".format(dir_path))
        os.makedirs(dir_path, exist_ok=True)
        for pt_dir in pt_dirs:
            pt_path = os.path.join(dir_path, pt_dir)
            LOG.debug("Creating directory: {}".format(pt_path))
            os.makedirs(pt_path, exist_ok=True)
    metasploit_rc_files(args.input)
    recon_ng_rc_files(args.input, args.domain)
    checklist(args.input)
    LOG.info("Directories have been created.")
    print("************* ")
    print(""" Now that the directories have been created, please put the in-scope ip addresses into a file named ips.txt.""")
    print(" Once done run the yaml_poc.py script to create the needed commands.")
    print("************* ")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Creates folder structure for engagement.',
        prog='folder_structure.py',
    )
    parser.add_argument('input', help='Full path to pentest folder. (ex: /root/pentests/tjcim)')
    parser.add_argument('domain', help='Domain')
    args = parser.parse_args(args)
    if args.input.endswith('/'):
        args.input = args.input[:-1]
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Set logger to debug.")
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
