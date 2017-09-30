""" Read in file and then extrapolate the ips based on cidr format and using dashes """
import os
import struct
import socket
import argparse


def cidr_to_ip_list(in_cidr):
    """ Accept IPs in cidr format and returns a list of IPs """
    (ip, cidr) = in_cidr.split('/')
    cidr = int(cidr)
    host_bits = 32 - cidr
    i = struct.unpack('>I', socket.inet_aton(ip))[0]  # note the endianness
    start = ((i >> host_bits) << host_bits) + 1  # clear the host bits
    end = i | ((1 << host_bits) - 1)
    ips = []
    for i in range(start, end):
        ips.append(socket.inet_ntoa(struct.pack('>I', i)))
    return ips


def dashed_ips_to_list(in_dashed):
    """ Accept IPs in dashed format and return list of ips """
    ips = []
    (start, end) = in_dashed.split('-')
    first_three_octets = start.rsplit('.', 1)[0]
    last_octet = int(start.split('.')[3])
    ips.append(start)
    while last_octet < int(end):
        last_octet += 1
        ip = first_three_octets + '.' + str(last_octet)
        ips.append(ip)
    return ips


def extract_ips(input_file, output_dir):
    out_ips = []
    with open(input_file) as f:
        for line in f:
            if len(line.strip().split('-')) > 1:
                print(line.strip(), 'dashed')
                out_ips.extend(dashed_ips_to_list(line.strip()))
            elif len(line.strip().split('/')) > 1:
                print(line.strip(), 'cidr')
                out_ips.extend(cidr_to_ip_list(line.strip()))
            else:
                print(line.strip(), 'single ip')
                out_ips.append(line.strip())
    output_file_name = os.path.join(output_dir, '_ips.txt')
    with open(output_file_name, 'w') as f:
        f.write('\r\n'.join(out_ips))


def parse_args():
    parser = argparse.ArgumentParser(description='Extract IPs from IP notation in a file.')
    parser.add_argument('input_file', help='a file with ips listed in cidr or dashed format')
    parser.add_argument('output_dir', help='directory to write ips.txt file')
    return parser.parse_args()


if __name__ == '__main__':
    extract_ips(parse_args().input_file, parse_args().output_dir)
