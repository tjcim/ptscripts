import os
import time
import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
file_path = os.path.expanduser(args.filename)


with open(file_path) as fp:
    for line in fp:
        line = line.strip(' \t\n\r')
        print(line)
        subprocess.call(['xdg-open', line])
        time.sleep(1)
