import os
# import filecmp

from ptscripts import create_webserver_list as cwl
from ptscripts.tests.test_utilities import two_files_contain_same_info


def test_create_webserver_list(ports_csv, webserver_file, tmpdir):
    """ This will function test the script. """
    # Run script
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "webservers.txt")
    expected_path = webserver_file
    args = cwl.parse_args([ports_csv, output_dir])
    cwl.main(args)

    # compare
    assert two_files_contain_same_info(output_file, expected_path)
