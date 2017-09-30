import os
import argparse
import subprocess
import ipaddress


parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
file_path = os.path.expanduser(args.filename)

print("~ Filename: {}".format(file_path))
with open(file_path) as fp:
    for line in fp:
        line = line.strip(' \t\n\r')
        print(line)
        subprocess.call(['enum4linux', '-a', line])
