import argparse
import subprocess
from urlparse import urlparse
from ptscripts.iframe import write_iframe


parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("url")
args = parser.parse_args()
url_netloc = urlparse(args.url).netloc

folder_path = '/root/pentests/{}/'.format(args.name)
file_path = '/root/pentests/{}/commands.txt'.format(args.name)
aha_command = ["aha", "-b"]
commands = []
commands.append((["wafw00f", "-av", "{}".format(args.url)], aha_command))
commands.append((["nmap", "-v", "-A", "-Pn", "{}".format(url_netloc)], aha_command))
commands.append((["whatweb", "-v", "-a", "4", args.url], aha_command))
commands.append((["nikto", "-host", args.url], aha_command))
commands.append((["testssl.sh", args.url], aha_command))

for command in commands:
    print("\r\n")
    print("**************************")
    print("Running: {}".format(command[0][0]))
    print("**************************")
    p1 = subprocess.Popen(command[0], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['tee', '/dev/tty'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(command[1], stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    output = p3.communicate()[0]
    file_name = "{}{}_{}.html".format(folder_path, command[0][0], url_netloc)
    with open(file_name, 'w') as file_handler:
        file_handler.write(output)

print("Running iFrame")
write_iframe(args.url, folder_path)
