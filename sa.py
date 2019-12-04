#!/usr/bin/env python
"""
This script is used to quickly identify the network information. It will print out the IP address,
network address, gateway address, dns servers, it will run an nbtquery for active directory dcs.
It also runs an arp scan, and ping scan saving the results to a hosts.txt file.

Arguments:
    output: full path to pentest folder
    interface: what interface to use, defaults to eth0
"""
import os
import socket
import logging
import ipaddress
import subprocess

import click
from requests import get
import netifaces as ni


HOSTS_FILE = "sa_hosts.txt"
COMMANDS_FILE = "sa_commands.txt"
SA_RESUTS_FILE = "sa_results.txt"


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        log.debug(f"AttributeError socket.inet_pton({socket.AF_INET}, {address})")
        try:
            socket.inet_aton(address)
        except socket.error:
            log.debug(f"socket.error socket.inet_aton({address})")
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        log.debug(f"socket.error socket.inet_pton({socket.AF_INET}, {address})")
        return False
    return True


def get_dns_ips():
    # TODO: Get this to run cat /etc/resolv.conf saving the output as a screenshot
    log.info(f"Reading /etc/resolv.conf to get DNS server")
    dns_ips = []
    with open('/etc/resolv.conf') as fp:
        for _, line in enumerate(fp):
            columns = line.split()
            if columns[0] == 'nameserver':
                ip = columns[1:][0]
                if is_valid_ipv4_address(ip):
                    dns_ips.append(ip)
    log.debug(f"Found the following DNS IPs {', '.join(dns_ips)}")
    return dns_ips


def get_domain_names():
    log.info(f"Reading /etc/resolv.conf to get domain names")
    domain_names = []
    with open('/etc/resolv.conf') as fp:
        for _, line in enumerate(fp):
            columns = line.split()
            if columns[0] == 'search':
                domain_names.append(columns[1:][0])
    log.debug(f"Found the following domains {', '.join(domain_names)}")
    return domain_names


def get_domain_controllers(domain_names, commands, output):
    # TODO: Get this to run the command saving the output and creating a screenshot
    log.info("Querying the network for domain controllers.")
    domain_controllers = []
    for domain in domain_names:
        for ending in ["", ".com", ".local"]:
            args = ["nslookup", "-type=srv", f"_ldap._tcp.dc._msdcs.{domain}{ending}"]
            commands.append(" ".join(args))
            nslookup_results = subprocess.run(args, capture_output=True, text=True)
            for line in nslookup_results.stdout.splitlines():
                if line.startswith("_ldap"):
                    domain_controllers.append(line.split()[6][:-1])  # Just get the hostname
    if not domain_controllers:
        domain_controllers.append("No Domain Controllers found.")
    else:
        with open(os.path.join(output, "dcs.txt"), "w") as fp:
            fp.write("\n".join(domain_controllers))
            fp.write("\n")
    log.debug(f"Domain Controllers: {', '.join(domain_controllers)}")
    return domain_controllers, commands


def ping_scan(subnet, hosts, commands):
    # TODO: Get this to run the command saving the output and creating a screenshot
    # expects that hosts is a set
    log.info(f"Running an nmap ping scan on the subnet: {subnet}")
    args = ["nmap", "-sn", "-PS", "-n", subnet]  # Ping scan, TCP SYN/ACK, No DNS resolution
    commands.append(" ".join(args))
    nmap_results = subprocess.run(args, capture_output=True, text=True)
    for line in nmap_results.stdout.splitlines():
        if line.startswith("Nmap scan"):
            hosts.add(line.split()[4])  # Just get the IP address
    log.debug(f"Nmap ping scan done. Found {len(hosts)} ips.")
    return hosts, commands


def nbt_scan(subnet, hosts, commands):
    # TODO: Get this to run the command saving the output and creating a screenshot
    # expects that hosts is a set
    log.info(f"Running an nbtscan on the subnet: {subnet}")
    args = ["nbtscan", "-q", subnet]
    commands.append(" ".join(args))
    nbtscan_results = subprocess.run(args, capture_output=True, text=True)
    for line in nbtscan_results.stdout.splitlines():
        hosts.add(line.split()[0])
    log.debug(f"nbtscan done. Hosts now contains {len(hosts)} ips")
    return hosts, commands


def arp_scan(interface, hosts, commands):
    # TODO: Get this to run the command saving the output and creating a screenshot
    # expects that hosts is a set
    log.info(f"Running an arp-scan on the interface: {interface}")
    args = ["arp-scan", "-q", "-I", interface, "--localnet"]
    commands.append(" ".join(args))
    arp_results = subprocess.run(args, capture_output=True, text=True)
    for line in arp_results.stdout.splitlines():
        try:
            ip = line.split()[0]
        except IndexError:
            continue
        if is_valid_ipv4_address(ip):
            hosts.add(ip)
    log.debug(f"arp-scan done. Hosts now contains {len(hosts)} ips")
    return hosts, commands


def get_external_ip():
    log.info("Getting external IP from api.ipify.org")
    external_ip = get('https://api.ipify.org').text
    log.debug(f"External IP = {external_ip}")
    return external_ip


def get_if_ip_info(commands, interface):
    log.info(f"Getting IP address for {interface}")
    commands.append("ip addr")
    ip_address = ni.ifaddresses(interface)[ni.AF_INET][0]["addr"]
    log.debug(f"IP address for {interface} is {ip_address}")
    log.debug(f"Getting netmask for {interface}")
    netmask = ni.ifaddresses(interface)[ni.AF_INET][0]["netmask"]
    log.debug(f"Netmask for {interface} is {netmask}")
    network = ipaddress.IPv4Network(f"{ip_address}/{netmask}", strict=False)
    log.debug(f"Network address {network.network_address}")
    cidr = network.compressed.split("/")[1]
    log.debug(f"Network subnet {network.compressed}, cidr = {cidr}")
    gateway = ni.gateways()['default'][ni.AF_INET][0]
    log.debug(f"Gateway address {gateway}")
    commands.append("cat /etc/resolv.conf")
    return ip_address, netmask, network, cidr, gateway, commands


def write_hosts(output, hosts):
    log.info(f"Writing IPs found to {os.path.join(output, HOSTS_FILE)}")
    with open(os.path.join(output, HOSTS_FILE), "w") as fp:
        fp.write("\n".join(hosts))
        fp.write("\n")


def write_commands(output, commands):
    log.info(f"Writing commands run to {os.path.join(output, COMMANDS_FILE)}")
    with open(os.path.join(output, COMMANDS_FILE), "w") as fp:
        fp.write("\n".join(commands))
        fp.write("\n")


def main(output, interface):
    commands = []
    log.info(f"Running sa on interface {interface}")
    ip_address, netmask, network, cidr, gateway, commands = get_if_ip_info(commands, interface)
    external_ip = get_external_ip()
    dns_ips = get_dns_ips()
    domain_names = get_domain_names()
    domain_controllers, commands = get_domain_controllers(domain_names, commands, output)
    hosts, commands = ping_scan(network.compressed, set(), commands)
    hosts, commands = nbt_scan(network.compressed, hosts, commands)
    hosts, commands = arp_scan(interface, hosts, commands)
    log.info(f"Writing sa results to {os.path.join(output, SA_RESUTS_FILE)}")
    with open(os.path.join(output, SA_RESUTS_FILE), "w") as fp:
        fp.write(f"IP Address: {ip_address}\n")
        fp.write(f"Net Mask: {netmask}\n")
        fp.write(f"CIDR: {cidr}\n")
        fp.write(f"Network Address: {network.network_address}\n")
        fp.write(f"DNS Servers: {', '.join(dns_ips)}\n")
        fp.write(f"External IP: {external_ip}\n")
        fp.write(f"Domain Controllers: {', '.join(domain_controllers)}\n")
        fp.write(f"Domain Names: {', '.join(domain_names)}\n")
        fp.write(f"Gateway IP: {gateway}\n")
    write_hosts(output, hosts)
    write_commands(output, commands)
    print("-----------------------------")
    print(f"IP Address: {ip_address}")
    print(f"Net Mask: {netmask}")
    print(f"CIDR: {cidr}")
    print(f"Network Address: {network.network_address}")
    print(f"DNS Servers: {', '.join(dns_ips)}")
    print(f"External IP: {external_ip}")
    print(f"Domain Controllers: {', '.join(domain_controllers)}")
    print(f"Domain Names: {', '.join(domain_names)}")
    print(f"Gateway IP: {gateway}")
    print("-----------------------------")


@click.command()
@click.option("-v", "--verbose", "verbocity", flag_value="verbose",
              help="-v Will show DEBUG messages.")
@click.option("-q", "--quiet", "verbocity", flag_value="quiet",
              help="-q Will show only ERROR messages.")
@click.option("-o", "--output", prompt=True,
              type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
              help="The path where the information will be saved.")
@click.option("-i", "--interface", default="eth0", help="Interface to use, default is eth0")
def cli(verbocity, output, interface):
    """This script performs a series of commands to provide information on the environment."""
    if verbocity == "verbose":
        log.setLevel("DEBUG")
        log.debug("Setting logging level to DEBUG")
    elif verbocity == "quiet":
        log.setLevel("ERROR")
        log.error("Setting logging level to ERROR")
    else:
        log.setLevel("INFO")
        log.info("Setting logging level to INFO")
    main(output, interface)


logging.basicConfig(
    format="{asctime} [{levelname}] {message}",
    style="{", datefmt="%H:%M:%S",
)
log = logging.getLogger()

if __name__ == "__main__":
    cli()  # pylint:disable=no-value-for-parameter
