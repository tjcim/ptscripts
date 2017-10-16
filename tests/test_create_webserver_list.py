import os
# import filecmp

from ptscripts import create_webserver_list as cwl
from ptscripts.tests.test_utilities import TEST_FILE_PATH, two_files_contain_same_info


def test_create_webserver_list(tmpdir):
    """ This will function test the script. """
    # Run script
    input_file = os.path.join(TEST_FILE_PATH, "ports.csv")
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "webservers.txt")
    expected_path = os.path.join(TEST_FILE_PATH, "webservers.txt")
    args = cwl.parse_args([input_file, output_dir])
    cwl.build_webservers_file(args)

    # compare
    assert two_files_contain_same_info(output_file, expected_path)
