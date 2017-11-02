import os
import shutil
import argparse
import logging

from config import config
from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.folder_structure")


def metasploit_rc_files(pentest_dir):
    pentest_name = os.path.split(pentest_dir)
    if pentest_name is None:
        pentest_name = os.path.split(os.path.split(pentest_dir)[0])[1]
    # metasploit workspace and import nmap
    discovery_folder = os.path.join(pentest_dir, "ept/discovery/rc_files")
    os.makedirs(discovery_folder, exist_ok=True)
    LOG.info("Creating the db_import.rc file in {}".format(discovery_folder))
    workspace_import_path = os.path.join(discovery_folder, "db_import.rc")
    nmap_xml = os.path.join(pentest_dir, "ept/discovery/nmap/ss_all.xml")
    with open(workspace_import_path, "w") as f:
        f.write("workspace -a {}\n".format(pentest_name))
        f.write("db_import {}\n".format(nmap_xml))
        f.write("hosts")

    # endpointmapper
    enumeration_folder = os.path.join(pentest_dir, "ept/enumeration/rc_files")
    os.makedirs(enumeration_folder, exist_ok=True)
    LOG.info("Creating the endpoint_mapper.rc file in {}".format(enumeration_folder))
    endpoint_resource_file = os.path.join(enumeration_folder, "endpoint_mapper.rc")
    with open(endpoint_resource_file, "w") as f:
        f.write("use auxiliary/scanner/dcerpc/endpoint_mapper\n")
        f.write("hosts -R\n")
        f.write("set THREADS 10\n")
        f.write("show options\n")
        f.write("exploit")

    # smtp_relay
    exploitation_folder = os.path.join(pentest_dir, "ept/exploitation/rc_files")
    os.makedirs(exploitation_folder, exist_ok=True)
    LOG.info("Creating the smtp_relay.rc file in {}".format(exploitation_folder))
    smtp_resource_path = os.path.join(exploitation_folder, "smtp_relay.rc")
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
    base_dirs = ["ept", "ipt", "macros", "physical", "report", "social", "wireless", "webapp"]
    pt_dirs = ["discovery", "enumeration", "exploitation", "footprinting", "ips", "post", "screenshots"]
    LOG.info("Creating directories")
    for directory in base_dirs:
        dir_path = os.path.join(args.input, directory)
        LOG.debug("Creating directory: {}".format(dir_path))
        os.makedirs(dir_path, exist_ok=True)
    for directory in ["ept", "ipt"]:
        for pt_dir in pt_dirs:
            LOG.debug("Creating directory: {}".format(dir_path))
            dir_path = os.path.join(os.path.join(args.input, directory), pt_dir)
            os.makedirs(dir_path, exist_ok=True)
    metasploit_rc_files(args.input)
    checklist(args.input)
    LOG.info("Directories have been created.")
    print("************* ")
    print(""" Now that the directories have been created, please put the in-scope ip addresses in the ips/ips.txt file.""")
    print(" Once done run the yaml_poc.py script to create the needed commands.")
    print("************* ")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Creates folder structure for engagement.',
        prog='folder_structure.py',
    )
    parser.add_argument('input', help='Path to pentest folder.')
    args = parser.parse_args(args)
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
