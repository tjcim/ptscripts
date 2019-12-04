# Notes and TODOs

* I should mark all the scripts as executable and include the proper shebang
* The tests have to be rebuilt. I have fallen out of using them and should resolve that.
* I need to switch over the bash commands to use utils/run_commands as it works much better.
* I will need to figure out how to kill a command properly as it looks like my current attempts to timeout don't actually do that.

# Change Log

* 12/4/2019 - I am going to slowly switch all the scripts to use click as the cli instead of argparse
* 12/7/2017 - I am not happy with the way I currently run bash commands and get output, I created a couple of new functions in utils/run_commands.py that seems to work well. I have started switching over a few of the scripts web_nikto and dirb_image have both been switched.
* 11/14/2017 - Updated multi_nikto.py script to use threading and a few other command options to increase the speed.
* 11/9/2017 - Updated website_screenshot.py script to use threading as well as logic to reduce duplicate/unneeded images. Also it will resume now.
* 10/29/2017 - **Major changes, make sure you read the instructions below.**
* 10/27/2017 - Restructured scripts to oranize them in PTES phases
* 10/26/2017 - Changed website_screenshot to use requests first, if a response is provied other than a 404/403 error than it is passed to selenium
* 10/18/2017 - Refactored multi scripts and added unit tests
* 10/16/2017 - Added function test for parse_nessus_csv.py, changed nmap to output a ton more info.
* 10/15/2017 - Added documentation to some scripts and reformatted a couple of scripts to better allow for testing.
* 10/12/2017 - Added parse_nessus_csv.py. Extracts and formats vulnerabilities from the nessus csv file.
* 10/11/2017 - Updated web_commands.py it should work now. Switched multi_ike with pikebrute in print_commands.py

# Getting your environment set up

## Clone the Repo and install requirements

Make sure you have python3-venv installed.

    apt install python3-venv phantomjs aha libxml2-utils -y

Get the latest geckodriver release: https://github.com/mozilla/geckodriver/releases

    cd ~/Downloads
    tar -xvzf geckodriver*
    chmod a+x geckodriver
    mv geckodriver /usr/local/bin/

Clone this repo and then cd into the created directory. The commands below assume you are currently in the repo's directory.

    cd /opt && git clone htps://github.com/tjcim/ptscripts.git && cd ptscripts

Create a python virtual environment

    python3 -m venv env

Activate the virtual environment just created.

    source env/bin/activate

Install the required python packages

    pip install -r requirements.txt

## Edit the Config file

Copy the config.py.sample to config.py

Edit the config.py file and replace with the correct information for your environment.

## Pentest folder prep

Create a folder for the pentest you are conducting. I like to store the pentests in /root/pentests/*name*. Name should be a shortname without spaces for example, if I was doing a pentest for ACME - I would create a acme folder at /root/pentests/acme/.

For an external pentest: Once pentest folder is setup run `python /opt/ptscripts/folder_structure <pentest folder path>`

~~This will create a bunch of folders with the PTES phases in mind.~~ Once the folders have been created, place a file in the `ept/ips` folder with the in-scope ips (in the formats supported below). Then run the `yaml_poc.py` file. This is a proof of concept that I will be moving to primetime and removing the old `print_commands.py` file.

## ip file

The script will extract individual ips, each entry should be on a line by itself. Extraction is done from either a dashed (192.168.1.1-32 or 192.168.1.1-192.168.1.22) or a cidr (192.169.1.1/24). You can also include individual ips.

example - all of these can be interpreted by the script:

    192.168.1.32-64
    192.168.2.32-192.168.1.64
    192.168.3.0/24
    192.168.4.154

The script will create a file named `_ips.txt` within the `{pentest_folder}/ept/ips/` folder.. This text file will have each ip listed individually. The reason we use individual IPs is because some commands are able to parse cidr and dashed ips and some are not. In addition, some commands expect a single IP. So, we create a file with the lowest common denominator in mind.

# Running the scripts

## yaml_poc.py

    python yaml_poc.py

It is recommended that the `yaml_poc.py` script is run first. Be sure you have the virtual environment activated and then run the script and answer the questions. The script needs to know the pentest folder name - following the example above I would provide `levis` (path is configured in `config.py`), the ip file name as well as the domain name (used for dns stuff).

This script will create a `{pentest_folder}/ept/yaml_commands.txt` file.

**Adding commands**

I moved the commands to a yaml file named `commands.yaml` (in the commands folder). This is to encourage others to add their commands to the file to extend the capabilities.

## yaml_commands.txt

This file will provide default commands that you can copy and paste into the terminal. Every command listed should produce an output that is saved into the appropriate pentest folder. It is important that the commands that create text files are run before they are required. For example, the first command listed in the `yaml_commands.txt` file will be the `ip_extract.py` command. This is what takes the ips and breaks them up into the `_ips.txt` file that is used in later commands. So in general, follow the order of the commands from the `yaml_commands.txt` file unless you know what you are doing.
