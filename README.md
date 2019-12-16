# Notes and TODOs

* Combine the `int_initial.py`, `ext_initial.py` and `web_initial.py` scripts
* I should mark all the scripts as executable and include the proper shebang
* The tests have to be rebuilt. I have fallen out of using them and should resolve that.

# Change Log

* 12/15/2019 - Added the `int_initial.py` script, it nees a lot of work still. Fixed an issue with the `sa.py` script.
* 12/11/2019 - Fixed the `http_methods.py` file. But it needs a bit more work. I want to make it accept a single url (done), a text file of urls, and the csv output from `nmap_to_csv.py`. ~~Second, I need to figure out how to take a picture of the console output.~~ (done, but a bit hacky)
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

Start with either the `ept_initial.py` or `web_initial.py` file. This will create the folder structure and a list of commands to be run.

For EPTs make sure to put the IPs in a file named ips.txt in the ept folder.

### ip file

The script will extract individual ips, each entry should be on a line by itself. Extraction is done from either a dashed (192.168.1.1-32 or 192.168.1.1-192.168.1.22) or a cidr (192.169.1.1/24). You can also include individual ips.

example - all of these can be interpreted by the script:

    192.168.1.32-64
    192.168.2.32-192.168.1.64
    192.168.3.0/24
    192.168.4.154

The script will create a file named `_ips.txt` within the `{pentest_folder}/ept/ips/` folder.. This text file will have each ip listed individually. The reason we use individual IPs is because some commands are able to parse cidr and dashed ips and some are not. In addition, some commands expect a single IP. So, we create a file with the lowest common denominator in mind.

# Running the scripts

## ept_initial.py

    python ept_initial.py -o /root/pentests/acme -d acme.org

**Adding commands**

I moved the commands to a yaml file named `commands.yaml` (in the commands folder). This is to encourage others to add their commands to the file to extend the capabilities.
