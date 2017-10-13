import os
import time

import config
from utils import dir_exists


def create_command_file(command_file, pentest_dir_name, proxy):
    """ Creates a new command file. """
    if proxy:
        proxy_text = ' -- using proxy'
    else:
        proxy_text = ' no proxy'
    with open(command_file, "w") as f:
        statement = '# Pentest commands for {} created {} {}\r\n'.format(
            pentest_dir_name,
            time.strftime('%I:%M%p %Z on %b %d, %Y'),
            proxy_text
        )
        f.write(statement)
        f.write('# ' + ('*' * len(statement)) + '\r\n\r\n')


def write_comment_to_file(comment, command_file):
    """ Writes a comment about the following command. """
    if config.PRINT_COMMENTS:
        com = "# " + comment + '\r\n'
        with open(command_file, "a") as f:
            f.write(com)


def write_command_to_file(command, command_file):
    """ Writes command to file. """
    command_text = command + '\r\n\r\n'
    with open(command_file, "a") as f:
        f.write(command_text)


def get_pentest_info():
    """ Ask questions to get information for pentest. """
    pentest_dir_name = input('Pentest directory name? ')  # noqa: F821
    domain_name = input('Domain for dnsrecon? ')  # noqa: F821
    ip_file_name = input('Name of ip file [ips.txt]: ') or "ips.txt"  # noqa: F821
    use_proxy = bool(input('Use proxy [False]: '))
    return (pentest_dir_name, domain_name, ip_file_name, use_proxy)


def run_print_commands():  # noqa pylint: disable=too-many-locals,too-many-statements
    """ Print commands to file. """
    pentest_dir_name, domain_name, ip_file_name, use_proxy = get_pentest_info()  # pylint: disable=unused-variable

    pentest_path = os.path.join(config.BASE_PATH, pentest_dir_name)
    resource_path = os.path.join(pentest_path, 'rc_files')
    command_file = os.path.join(pentest_path, 'commands.txt')
    create_command_file(command_file, pentest_dir_name, use_proxy)

    # This allows the user to put the pentest_dir_name as something like company/external
    # and another as company/internal. All commands will work the same except for the
    # metasploit workspace and the nessus scan name will be company_external and
    # company_internal.
    if '/' in pentest_dir_name:
        workspace_name = pentest_dir_name.replace('/', '_')
    else:
        workspace_name = pentest_dir_name

    def write_command(command):
        write_command_to_file(command, command_file)

    def write_comment(comment):
        write_comment_to_file(comment, command_file)

    def pj(script):
        """ Shorthand script for path.join """
        return os.path.join(config.SCRIPTS_PATH, script)

    def pyscript(script, in_file, out_dir=None, aha=False, use_proxy=False, line_fix=False):  # pylint: disable=too-many-arguments
        """ Shorthand function to return python <script> in out """
        command = "python {script} {in_file}{out_dir}{proxy}{aha}".format(
            script=pj(script),
            in_file=in_file,
            out_dir=" " + out_dir if out_dir else "",
            proxy=" --proxy" if use_proxy else "",
            aha=" | tee /dev/tty | aha -b {}> {}".format(
                "--line-fix " if line_fix else "",
                out_dir if out_dir else ""
            ) if aha else "",
        )
        return command

    # Create directories
    dir_exists(resource_path, True)

    # Extract IPs from cidr/dashed to file:
    orig_ip_path = os.path.join(pentest_path, ip_file_name)
    extract_command = pyscript("ip_extract.py", orig_ip_path, pentest_path)
    write_command(extract_command)
    ips_text = os.path.join(pentest_path, '_ips.txt')

    # nessus scan
    write_comment('Make sure nessus is accessible via {} (configurable through config file)'.format(config.NESSUS_URL))
    nessus_command = pyscript('nessus_scan.py', ips_text, workspace_name)
    write_command(nessus_command)

    # nmap
    nmap_out = os.path.join(pentest_path, "nmap")
    nmap_xml = os.path.join(pentest_path, "nmap.xml")
    nmap_html = os.path.join(pentest_path, "nmap.html")
    nmap_command = "nmap -sS -sU -v --script banner -sV --version-light -Pn -p U:631,161,123,138,137,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69,5353,111,49154,1701,998,996,997,999,3283,49153,1812,136,2222,2049,3278,5060,1025,1433,3456,80,20031,1026,7,1646,1645,593,518,2048,31337,515,T:[1-65535] -oA {} -iL {} --min-hostgroup 128 --defeat-rst-ratelimit | tee /dev/tty | aha -b > {}".format(nmap_out, ips_text, nmap_html)
    write_command(nmap_command)

    # csv file
    csv_path = os.path.join(pentest_path, 'ports.csv')
    csv_command = pyscript('nmap_to_csv.py', nmap_xml, pentest_path)
    write_comment('Creates a ports.csv file with just the open ports.')
    write_command(csv_command)

    # webservers list
    webserver_path = os.path.join(pentest_path, "webservers.txt")
    webserver_command = pyscript("create_webserver_list.py", csv_path, pentest_path)
    write_comment('Creates a webservers.txt file with a list of every URL found.')
    write_command(webserver_command)

    # webserver screenshots
    screenshot_path = os.path.join(pentest_path, "website_screenshots")
    screenshot_command = pyscript("website_screenshot.py", webserver_path, screenshot_path, use_proxy=use_proxy)
    write_comment('Uses phantomjs to open each URL found and takes a picture of it and saves it in the website_screenshots folder.')
    write_command(screenshot_command)

    # metasploit workspace and import nmap
    workspace_import_path = os.path.join(resource_path, "db_import.rc")
    with open(workspace_import_path, "w") as f:
        f.write("workspace -a {}\n".format(workspace_name))
        f.write("db_import {}\n".format(nmap_xml))
        f.write("hosts")
    metasploit_workspace_command = 'msfconsole -r {}'.format(workspace_import_path)
    write_comment('Creates a metasploit workspace and imports the hosts found using the nmap.xml file.')
    write_command(metasploit_workspace_command)

    # dnsrecon
    write_comment('This will only run with python < 3 right now. So make sure the virtualenv is deactivated prior to running this command.')
    dnsrecon_html = os.path.join(pentest_path, "dnsrecon_{}_.html".format(domain_name))
    dnsrecon_command = 'dnsrecon -d {0} -D /usr/share/wordlists/dnsmap.txt | tee /dev/tty | aha -b > {1}'.format(domain_name, dnsrecon_html)
    write_command(dnsrecon_command)

    # rawr
    rawr_command = "rawr.py {} --rd --dns -orx --downgrade --spider -d {}".format(nmap_xml, pentest_path)
    write_command(rawr_command)

    # yasuo
    yasuo_html = os.path.join(pentest_path, "yasuo.html")
    if use_proxy:
        yasuo_command = "proxychains yasuo.rb -s /opt/yasuo/signatures.yaml -f {} -t 10 | tee /dev/tty | aha -b > {}".format(nmap_xml, yasuo_html)
    else:
        yasuo_command = "yasuo.rb -s /opt/yasuo/signatures.yaml -f {} -t 10 | tee /dev/tty | aha -b > {}".format(nmap_xml, yasuo_html)
    write_command(yasuo_command)

    # multi_enum4linux
    enum4linux_html = os.path.join(pentest_path, "enum4linux.html")
    enum4linux_command = pyscript("multi_enum4linux.py", csv_path, enum4linux_html, aha=True, use_proxy=use_proxy, line_fix=True)
    write_comment('Runs the enum4linux command on each IP.')
    write_command(enum4linux_command)

    # multi_wpscan
    wpscan_html = os.path.join(pentest_path, "wpscan.html")
    wpscan_update_command = "wpscan --update"
    wpscan_command = pyscript("multi_wpscan.py", webserver_path, wpscan_html, aha=True)
    write_command(wpscan_update_command)
    write_comment('Runs the wpscan command for every URL found.')
    write_command(wpscan_command)

    # multi_nikto
    nikto_dir_path = os.path.join(pentest_path, "nikto")
    nikto_command = pyscript("multi_nikto.py", csv_path, nikto_dir_path, use_proxy=use_proxy)
    write_comment('Runs nikto for every URL found.')
    write_command(nikto_command)

    # endpointmapper
    endpoint_resource_file = os.path.join(resource_path, "endpoint_mapper.rc")
    with open(endpoint_resource_file, "w") as f:
        f.write("use auxiliary/scanner/dcerpc/endpoint_mapper\n")
        f.write("set RHOSTS file:{}\n".format(ips_text))
        f.write("set THREADS 10\n")
        f.write("show options\n")
        f.write("exploit")
    endpoint_command = "resource {}".format(endpoint_resource_file)
    write_comment('Run this from within metasploit')
    write_command(endpoint_command)

    # multi_testssl
    testssl_path = os.path.join(pentest_path, "testssl")
    testssl_command = pyscript("multi_testssl.py", webserver_path, testssl_path)
    write_comment('Runs testssl for every URL found.')
    write_command(testssl_command)

    # smtp_relay
    write_comment("Run this from the metasploit console.")
    smtp_resource_path = os.path.join(resource_path, "smtp_relay.rc")
    with open(smtp_resource_path, "w") as f:
        f.write("use auxiliary/scanner/smtp/smtp_relay\n")
        f.write("services -p 25 -R\n")
        f.write("show options\n")
        f.write("exploit")
    smtp_relay_command = "resource {}".format(smtp_resource_path)
    write_command(smtp_relay_command)

    # multi_whatweb
    whatweb_path = os.path.join(pentest_path, "whatweb")
    whatweb_command = pyscript("multi_whatweb.py", webserver_path, whatweb_path)
    write_comment('Runs whatweb for every URL found.')
    write_command(whatweb_command)

    # zap_attack
    zap_path = os.path.join(pentest_path, "zap")
    zap_command = pyscript("zap_attack.py", webserver_path, zap_path)
    write_comment('Make sure ZAP is up and running first.')
    write_command(zap_command)

    # burp requests
    burp_command = pyscript("burp_requests.py", webserver_path)
    write_comment("Make sure burp is running and is listening on port {}".format(config.BURP_PORT))
    write_command(burp_command)

    # open_websites
    open_websites_comments = "Opens each website in the default browser"
    open_websites_command = pyscript("open_websites.py", webserver_path)
    write_comment(open_websites_comments)
    write_command(open_websites_command)

    # pikebrute
    ike_path = os.path.join(pentest_path, "ike")
    ike_command = pyscript("pikebrute.py", csv_path, ike_path)
    write_command(ike_command)

    # hydra ftp
    # ftp_ips = get_ips_with_port_open(csv_path, 21)
    # for ip in ftp_ips:
    # write_command("hydra -L /usr/share/wordlists/metasploit/unix_users.txt -P /usr/share/wordlists/rockyou.txt -v {} ftp".format(ip))


if __name__ == '__main__':
    run_print_commands()
