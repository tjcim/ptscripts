"""
This file contains a list of command dictionaries that are used for testing.

A command is a dictionary object with the following entries: name, tags, command, comments. When processed, the tags will determine if the command is printed or not. For example if running a web app assessment, all the commands with the tag "web" will be included. The command entries are as follows.

    "name" : String
        Required - a unique name for the command to be run
    "tags" : List
        Required - A list of strings that state the type of pentest in which the command will be printed. (e.g. "web", "pentest")
    "comments" : List
        Optional - A list of strings that will be printed before the command if config.PRINT_COMMENTS is True.

Formatting a command. The available variables are:
    {pentest_path} - This is BASE_PATH/PENTEST_NAME and will store the output of the commands.
    {url} - The url to be tested.
    {netloc} - The netloc of the url... for example the url: https://www.google.com will have a netloc of www.google.com.
    {scripts_dir} - The path to the ptscripts directory
    {ips_name} - The name of the file that contains the ips. This file will be used as input to ip_extract.py

If comments are turned on (from config.py) any comments included are printed before the command.
"""
COMMANDS = [
    {
        "name": "ip_extract", "tags": ["pentest"],
        "command": "python {scripts_dir}/ip_extract.py {pentest_path}/{ips_file} {pentest_path}",
        "comments": [""],
    },
    {
        "name": "wafw00f", "tags": ["web"],
        "command": "wafw00f -av {url} | tee /dev/tty | aha -b > {output_dir}/wafw00f_{netloc}.html",
        "comments": [""],
    },
    {
        "name": "nmap", "tags": ["pentest"],
        "command": "nmap -sS -sU -v --script banner -sV --version-light -Pn -p U:631,161,123,138,137,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69,5353,111,49154,1701,998,996,997,999,3283,49153,1812,136,2222,2049,3278,5060,1025,1433,3456,80,20031,1026,7,1646,1645,593,518,2048,31337,515,T:[1-65535] -oA {output_dir}/nmap -iL {ips_file} --min-hostgroup 128 --defeat-rst-ratelimit | tee /dev/tty | aha -b > {output_dir}/nmap.html",
        "comments": [""],
    },
    {
        "name": "nmap", "tags": ["web"],
        "command": "nmap -v -A {url} | tee /dev/tty | aha -b > {output_dir}/nmap_{netloc}.html",
    },
    {
        "name": "whatweb", "tags": ["web"],
        "command": "whatweb -v -a 4 {url} | tee /dev/tty | aha -b > {output_dir}/whatweb_{netloc}.html",
    },
    {
        "name": "nikto", "tags": ["web"],
        "command": "nikto -host {url} | tee /dev/tty | aha -b > {output_dir}/nikto_{netloc}.html",
    },
    {
        "name": "testssl", "tags": ["web"],
        "command": "testssl.sh {url} | tee /dev/tty | aha -b > {output_dir}/testssl_{netloc}.html",
    },
    {
        "name": "iframe", "tags": ["web"],
        "command": "python {scripts_dir}/iframe.py {url} {output_dir}",
    },
    {
        "name": "uniscan", "tags": ["web"],
        "command": "uniscan -u {url} -qweds | tee /dev/tty | aha -b > {output_dir}/uniscan_{netloc}.html",
    },
    {
        "name": "dirb", "tags": ["web"],
        "command": "dirb /usr/share/dirbuster/wordlists/directory-list-lowercase-2.3-small.txt -w | tee /dev/tty | aha -b > {output_dir}/dirb_{netloc}.html",
    },
    {
        "name": "wpscan_update", "tags": ["pentest", "web"],
        "command": "wpscan --update",
    },
    {
        "name": "wpscan", "tags": ["web"],
        "command": "wpscan --batch --url {url} --enumerate at,tt,t,ap,u[1-100] | tee /dev/tty | aha -b > {output_dir}/wpscan_{netloc}.html",
    },
]
