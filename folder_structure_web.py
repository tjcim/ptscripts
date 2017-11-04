import os
import shutil
import argparse
import logging

from config import config
from utils import utils, logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.folder_structure_web")


def checklist(pentest_dir):
    src = os.path.join(config.SCRIPTS_PATH, "templates/web_checklist.txt")
    dst = os.path.join(pentest_dir, "web_checklist.txt")
    LOG.info("Writing checklist file to: {}".format(dst))
    shutil.copyfile(src, dst)
    src = os.path.join(config.SCRIPTS_PATH, "templates/web_workflow.txt")
    dst = os.path.join(pentest_dir, "web_workflow.txt")
    LOG.info("Writing workflow file to: {}".format(dst))
    shutil.copyfile(src, dst)


def main(args):
    base_dirs = [
        "a1_injection", "a2_auth_session", "a3_sde", "a4_xxe", "a5_access",
        "a6_security", "a7_xss", "a8_deserialize", "a9_vulnerable",
        "a10_log", "screenshots",
    ]
    LOG.info("Creating directories")
    for directory in base_dirs:
        dir_path = os.path.join(args.input, directory)
        LOG.debug("Creating directory: {}".format(dir_path))
        os.makedirs(dir_path, exist_ok=True)
    checklist(args.input)
    LOG.info("Directories have been created.")


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Creates folder structure for engagement.',
        prog='folder_structure_web.py',
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
