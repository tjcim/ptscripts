import os
import argparse
import logging

from utils import utils # noqa
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.folder_structure")


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
    ips_file = os.path.join(args.input, "ept/ips/ips.txt")
    with open(ips_file, 'a'):
        pass
    LOG.info("Directories have been created.")
    print("************* ")
    print(""" Now that the directories have been created, please put the in-scope ip addresses in the {} file.""".format(ips_file))
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
