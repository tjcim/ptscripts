import os


TEST_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_files")


def two_files_contain_same_info(a_file, b_file):
    """ Compare two files and return True if they contain the same info. """
    with open(a_file, "r") as a_file:
        a_contents = a_file.read()

    with open(b_file, "r") as b_file:
        b_contents = b_file.read()

    return a_contents == b_contents
