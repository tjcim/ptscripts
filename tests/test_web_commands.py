# Functional test
import os
import filecmp

from ptscripts import config
from ptscripts import web_commands as wc
from ptscripts.tests.test_utilities import TEST_FILE_PATH


def test_web_command(tmpdir):
    # Arguments
    url = "http://www.sample.org"
    output_dir = os.path.join(config.BASE_PATH, "test")
    output_file = os.path.join(tmpdir.strpath, "web_commands.txt")
    args = wc.parse_args([output_dir, output_file, url])

    # Expected
    expected_path = os.path.join(TEST_FILE_PATH, "web_commands.txt")

    # Run command
    wc.main(args)

    # Compare
    assert filecmp.cmp(output_file, expected_path)
