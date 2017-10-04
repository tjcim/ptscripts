import struct
import argparse


def run_big_ip_decoder(encoded_string):
    print("\n[*] String to decode: {}\n".format(encoded_string))
    (host, port, _) = encoded_string.split('.')
    (a, b, c, d) = [i for i in struct.pack("<I", int(host))]
    (e) = [e for e in struct.pack("<H", int(port))]
    port = "0x{:02x}{:02x}".format(e[0], e[1])
    decoded_host = '{}.{}.{}.{}'.format(a, b, c, d)
    decoded_port = str(int(port, 16))
    print("[*] Decoded Host and Port: {}:{}".format(decoded_host, decoded_port))
    return decoded_host, decoded_port


def parse_args():
    parser = argparse.ArgumentParser(prog='big_ip_decoder.py')
    parser.add_argument('input', help='Cookie string (eg: 110536896.20480.0000 )')
    return parser.parse_args()


if __name__ == '__main__':
    run_big_ip_decoder(parse_args().input)
