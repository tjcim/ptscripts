import os

from ptscripts import parse_nessus_csv as pnc
from ptscripts.tests.test_utilities import two_csvs_contain_same_info


# Functional test
def test_run_parse_nessus_csv(nessus_in_csv, parsed_nessus_csv, tmpdir):
    # args
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "parsed_nessus.csv")
    args = pnc.parse_args([nessus_in_csv, output_dir])

    # Run script
    pnc.run_parse_nessus_csv(args)

    # Compare output
    assert two_csvs_contain_same_info(output_file, parsed_nessus_csv)
