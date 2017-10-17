import os
import csv
# import filecmp


TEST_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_files")


def csv_to_dict(csv_file):
    """ Reads the csv file into a dictionary. """
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results


def two_files_contain_same_info(a_file, b_file):
    """ Compare two files and return True if they contain the same info. """
    with open(a_file, "r") as af:
        a_contents = af.readlines()
    with open(b_file, "r") as bf:
        b_contents = bf.readlines()
    return a_contents == b_contents


def two_csvs_contain_same_info(a_file, b_file):
    """ Compare two csvs by using a dict reader and then comparison. """
    a_dict = csv_to_dict(a_file)
    b_dict = csv_to_dict(b_file)
    return a_dict == b_dict
