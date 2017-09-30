import csv
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')
args = parser.parse_args()
file_input = os.path.expanduser(args.input)
file_output = os.path.join(os.path.expanduser(args.output), "webservers.txt")


with open(file_input, 'r') as f:
    reader = csv.reader(f)
    host_ports = list(reader)

webservers = []

for host_port in host_ports:
    if host_port[2] and "http" in host_port[2]:
        port = ""
        if host_port[3] == 'ssl':
            scheme = 'https'
        else:
            scheme = 'http'
        if not host_port[1] == "80":
            port = ":" + host_port[1]
        # if https and port 443 don't add the port info
        if (host_port[1] == '443') and (scheme == 'https'):
            port = ''
        webservers.append(scheme + "://" + host_port[0] + port + '/')

with open(file_output, 'w') as f:
    for webserver in webservers:
        f.write(webserver + '\r\n')
