"""
On my last internal pentest I ran into a situation where the company had a large internal network
and each network was separated into subnets of /24. The tools I found to check if the networks had
hosts was extremely slow. This is my attempt at creating a utility that will do some fast checking
of networks.

Example usage:

My box has an IP in the range of 10.1.3.0/24. I want to quickly find out if neighboring networks have
any live hosts. I run this script and tell it to start at 10.0.0.0 and go until 10.5.0.0. Using /24
for each network. I want to use 100 threads.

    python neighboring_networks.py -s 10.0.0.0 -e 10.5.0.0 -c 24 -t 100

For each subnet the script adds the first 5 network addresses of the range (10.0.0.1-5), and the last 5
(10.0.0.250-254), and then selects a random 10% of the available addresses in the range. Then it tries
to ping these addresses. Based on the ping responses I will have a good idea if there are hosts
on that network or not. It will not be perfect because we are relying on hosts to respond to ping
(they may not) and that a host exists within the randomly selected ips. It is a tradeoff between
speed and being thorough.
"""
# TODO: Check that the starting network and the ending network do not have host bits set
# TODO: Figure out how to get KeyboardInterrupt working

import os
import sys
import time
import queue
import random
import logging
import argparse
import threading

from utils import utils
from utils.ipnetwork import IPNetwork

LOG = logging.getLogger("ptscripts.neighbors")


def check_queue_size(q):
    while not q.empty():
        LOG.info(f'{q.qsize()} hosts left to check.')
        time.sleep(30)


def consume(q):
    """ Gets the next IP from the queue and pings it, then stores the results and marks the task as done."""
    while not q.empty():
        name = threading.currentThread().getName()
        LOG.debug(f"Thread: {name} getting host from queue[current size = {q.qsize()}] {time.strftime('%H:%M:%S')}")
        host = q.get()
        LOG.debug(f"Pinging host: {host}")
        res = os.system(f'ping -c 1 {host} >/dev/null 2>&1')
        if res == 0:
            LOG.info(f"Host {host} is alive.")
        LOG.debug(f"Thread: {name} finished queue[current size = {q.qsize()}] {time.strftime('%H:%M:%S')}")
        q.task_done()


def producer(networks, q):
    """ Selects the IPs to ping within each network and then puts them into the queue. """
    host_count = 0
    for network in networks:
        LOG.debug(f"Producer: working on network {network} queue[current size = {q.qsize()}] {time.strftime('%H:%M:%S')}")
        num_hosts = len(list(network.hosts()))
        # Select first 5 hosts add to queue if num_hosts > 10 else add them all
        if num_hosts > 10:
            hosts = list(network.hosts())[:5]
            for host in hosts:
                q.put(host)
                host_count += 1
        else:
            hosts = list(network.hosts())
            for host in hosts:
                q.put(host)
                host_count += 1
        # Select last 5 hosts add to queue
        if num_hosts > 10:
            hosts = list(network.hosts())[-5:]
            for host in hosts:
                q.put(host)
                host_count += 1
        # Select 10% of the rest of the hosts add to queue
        if num_hosts > 10:
            sample_hosts_len = network.size() // 10
            hosts = random.sample(list(network.hosts())[5:-5], sample_hosts_len)
            for host in hosts:
                q.put(host)
                host_count += 1
    return host_count


def separate_networks(start, end, cidr):
    """ Separates networks based on netmask. """
    networks = []
    start_net = IPNetwork(f'{start}/{cidr}')
    end = IPNetwork(f'{end}/{cidr}')
    working_net = start_net
    LOG.info(f'Start net: {start_net}')
    while working_net < end + 1:
        LOG.debug(f'Adding network {working_net}')
        networks.append(working_net)
        working_net = working_net + 1
    return networks


def main(args):
    LOG.info(f'Starting with network: {args.starting_network}')
    LOG.info(f'Ending with network: {args.end_network}')
    LOG.info(f'Working with a cidr notation of: {args.cidr}')
    networks = separate_networks(args.starting_network, args.end_network, args.cidr)
    LOG.info(f'A total of {len(networks)} networks will be checked.')
    q = queue.Queue()
    host_count = producer(networks, q)
    LOG.info(f'Pinging a total of {host_count} IPs')
    queue_checker = threading.Thread(target=check_queue_size, args=(q,))
    queue_checker.start()
    for i in range(args.threads):
        worker = threading.Thread(name="ConsumerThread-" + str(i), target=consume, args=(q,))
        worker.setDaemon(True)
        worker.start()
        time.sleep(0.5)

    worker.join()


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Find neighboring networks.',
    )

    parser.add_argument('-s', '--starting-network', help='Starting Network, e.g. 10.0.0.0', required=True)
    parser.add_argument('-e', '--end-network', help='End network, e.g. 10.5.0.0', required=True)
    parser.add_argument('-c', '--cidr', help='Netmask of each network expressed as a two digit number, e.g. 24',
                        required=True, type=int)
    parser.add_argument('-t', '--threads', help='Number of threads to use. Default 100', default=100,
                        type=int)
    # parser.add_argument('output', help="where to store results")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Logger set to debug.")
    else:
        logger.setLevel('INFO')

    args.starting_network = str(args.starting_network)
    args.end_network = str(args.end_network)
    args.cidr = str(args.cidr)
    return args


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
