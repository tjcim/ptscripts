# Functional test
import os

from ptscripts.config import config
from ptscripts import web_commands as wc


def test_web_command(tmpdir):
    # Arguments
    url = "http://www.sample.org"
    output_dir = tmpdir.strpath
    args = wc.parse_args([output_dir, url])

    # Expected
    expected_list = [
        "# Web Application Assessment commands created using version {}".format(config.VERSION),
        "#**************************************************************",
        "wafw00f -av http://www.sample.org | tee /dev/tty | aha -b > {}/wafw00f_www.sample.org.html".format(output_dir),
        "nmap -v -A http://www.sample.org | tee /dev/tty | aha -b > {}/nmap_www.sample.org.html".format(output_dir),
        "whatweb -v -a 4 http://www.sample.org | tee /dev/tty | aha -b > {}/whatweb_www.sample.org.html".format(output_dir),
        "nikto -host http://www.sample.org | tee /dev/tty | aha -b > {}/nikto_www.sample.org.html".format(output_dir),
        "testssl.sh http://www.sample.org | tee /dev/tty | aha -b > {}/testssl_www.sample.org.html".format(output_dir),
        "python /opt/ptscripts/iframe.py http://www.sample.org {}".format(output_dir),
        "uniscan -u http://www.sample.org -qweds | tee /dev/tty | aha -b > {}/uniscan_www.sample.org.html".format(output_dir),
        "dirb /usr/share/dirbuster/wordlists/directory-list-lowercase-2.3-small.txt -w | tee /dev/tty | aha -b > {}/dirb_www.sample.org.html".format(output_dir),
        "wpscan --update",
        "wpscan --batch --url http://www.sample.org --enumerate at,tt,t,ap,u[1-100] | tee /dev/tty | aha -b > {}/wpscan_www.sample.org.html".format(output_dir),
    ]

    # Run command
    wc.main(args)

    # Compare
    output_file = os.path.join(output_dir, "web_commands.txt")
    contents = []
    with open(output_file, "r") as f:
        for line in f:
            line = line.rstrip()
            if line:
                contents.append(line)
    assert contents == expected_list
