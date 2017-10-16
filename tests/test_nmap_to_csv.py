import os

from ptscripts import nmap_to_csv as ntc
from ptscripts.tests.test_utilities import two_files_contain_same_info, TEST_FILE_PATH


# Functional Test
def test_nmap_to_csv(tmpdir):
    # args
    input_file = os.path.join(TEST_FILE_PATH, "nmap.xml")
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "ports.csv")
    expected_file = os.path.join(TEST_FILE_PATH, "ports.csv")
    print(input_file, output_dir)
    args = ntc.parse_args([input_file, output_dir])

    # Run script
    ntc.parse_nmap(args)

    # compare with expected
    assert two_files_contain_same_info(output_file, expected_file)
