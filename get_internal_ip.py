import csv
import telnetlib
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup


import os
dir = os.path.normpath(os.path.join(os.path.abspath(__file__), '../'))


def mytelnet(host, port):
    tn = telnetlib.Telnet(host, port)
    tn.write(b'GET /images\r\n')
    tn.write(b'exit\r\n')
    try:
        html_resp = tn.read_all()
    except:
        return
    soup = BeautifulSoup(html_resp)
    redirect_tag = soup.find('a')
    try:
        href = redirect_tag.get('href')
        url_parts = urlparse(href)
        if not host == url_parts.netloc:
            f = open('internal_ips.txt', 'a')
            f.write('{0}:{1}\n'.format(host, url_parts.netloc))
            print("Possible internal ip: {0}:{1}".format(host, url_parts.netloc))
    except AttributeError:
        return


def read_targets(input_file):
    # Read input file
    targets = []
    with open(input_file, 'rt') as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[1]) == 80:
                p = row[0], row[1]
                targets.append(p)
    return targets


def main():
    parser = argparse.ArgumentParser(prog='ip_disc.py')
    parser.add_argument('input', help='List of hosts to check.  Format:(hostname/ip,port)')
    args = parser.parse_args()
    input_file = os.path.normpath(os.path.join(dir, args.input))
    target_list = read_targets(input_file)
    for target in target_list:
        mytelnet(target[0], int(target[1]))


if __name__ == '__main__':
    main()
