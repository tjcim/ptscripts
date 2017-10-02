create virtualenv

    python3 -m venv env

activate virtualenv

    source env/bin/activate

install requirements

    pip install -r requirements.txt
    apt install phantomjs

# Config file

Edit the config.py file and replace with the correct information for your environment.

# Pentest folder prep

Make sure you have a folder ready to go with a text file of the ips.

## ip file

The script will extract individual ips, each entry should be on a line by itself. Extraction is done from either a dashed (192.168.1.1-32) or a cidr (192.169.1.1/24). You can also include individual ips. Note that the dashed only lists the first 3 octets before the dash.

example - all of these can be interpreted by the script:

    192.168.1.32-64
    192.168.2.0/24
    192.168.3.154

The script will create a file named '_ips.txt' within the folder specified. This text file will have each ip listed individually. The reason is that some commands are able to parse cidr and dashed ips and some are not, In addition some commands expect a single IP. So we create a file with the lowest common denominator in mind.

# print_commands.py

Run the print_commands.py script and answer the questions. The script needs to know the pentest folder name and the ip_list file as well as the domain name (used for dns-recon).

# TODO

* Fix up the enum4linux file.
* ~Move the pentest base folder to the config file and update the print_commands file~
* Fix up web_commands script
* Create script to run after ports.csv has been created for things like ike_scan
* Add ability to use proxy in print_commands
  * Change nmap command to the appropriate settings
* Add ability to do something like starr/internal for when I am doing both an internal and external pentest
  * This causes a problem right now for things like db_import where I use the foldername directly
* Rewrite the website_screenshots script to take a picture when redirected and the end_url is in the url_list. Then skip it when it comes up. This way we don't connect to the non-https version get redirected to the https version and then drop it.
