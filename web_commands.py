import argparse
from urlparse import urlparse


parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("url")
args = parser.parse_args()
url_netloc = urlparse(args.url).netloc

folder_path = '/root/pentests/{}/'.format(args.name)
file_path = '/root/pentests/{}/commands.txt'.format(args.name)
commands = []
commands.append("wafw00f -av {} | tee /dev/tty | aha -b >{}wafw00f_{}.html".format(
    args.url, folder_path, url_netloc))
commands.append("nmap -v -A {0}| tee /dev/tty | aha -b >{1}nmap_{0}.html".format(
    url_netloc, folder_path))
commands.append("whatweb -v -a 4 {}| tee /dev/tty | aha -b >{}whatweb_{}.html".format(
    args.url, folder_path, url_netloc))
commands.append("nikto -host {}| tee /dev/tty | aha -b >{}nikto_{}.html".format(
    args.url, folder_path, url_netloc))
commands.append("testssl.sh {} | tee /dev/tty | aha -b >{}testssl_{}.html".format(
    args.url, folder_path, url_netloc))
commands.append("python /opt/myscripts/iframe.py {} {}".format(
    args.url, folder_path))

with open(file_path, 'w') as file_handler:
    for item in commands:
        file_handler.write("{}\n".format(item))
