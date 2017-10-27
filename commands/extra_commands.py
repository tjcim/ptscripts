"""

Proof of Concept
Read ports.csv and print out extra commands to run based on open port.

"""
from utils import csv_to_dict
from commands_by_port import commands


nmap_dict = csv_to_dict("/root/pentests/home/ports.csv")
for row in nmap_dict:
    if row['port'] in commands:
        print("# " + commands[row['port']]['header'])
        print("# ***************************")
        for command in commands[row['port']]['commands']:
            print(command.format(ip=row['ipv4']))
