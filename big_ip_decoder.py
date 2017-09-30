#!/usr/bin/env python

# example string: 110536896.20480.0000

import struct
import sys

if len(sys.argv) != 2:
    print("Usage: %s encoded_string" % sys.argv[0])
    exit(1)

encoded_string = sys.argv[1]
print("\n[*] String to decode: %s\n" % encoded_string)

(host, port, end) = encoded_string.split('.')

(a, b, c, d) = [ord(i) for i in struct.pack("<I", int(host))]

(e) = [ord(e) for e in struct.pack("<H", int(port))]
port = "0x%02X%02X" % (e[0],e[1])

print("[*] Decoded Host and Port: %s.%s.%s.%s:%s\n" % (a,b,c,d, int(port,16)))
