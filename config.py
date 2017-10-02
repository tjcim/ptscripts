import os


# Do not change this line
SCRIPTS_PATH = os.path.abspath(os.path.dirname(__file__))

# Set this to where your pentests are stored
BASE_PATH = '/root/pentests/'

PROXY_PORT = '9050'
# When using a proxy, how long should we wait before taking screenshot?
PROXY_SLEEP = 10

# Burp
BURP_PORT = '8080'
BURP_PROXIES = {
    'http': 'http://127.0.0.1:{}'.format(BURP_PORT),
    'https': 'http://127.0.0.1:{}'.format(BURP_PORT),
}

# ZAP - API is found in settings > API
ZAP_PORT = '8081'
ZAP_API = 'eh343fe1ut18dgfsr2c9hs2nfk'
ZAP_PROXIES = {
    'http': 'http://127.0.0.1:{}'.format(ZAP_PORT),
    'https': 'http://127.0.0.1:{}'.format(ZAP_PORT),
}

# Nessus - API keys are found in settings > My Account
NESSUS_URL = 'https://10.0.0.29:8834'
NESSUS_ACCESS_KEY = '8a4b7dac6827c2a9fd9506788810f23611a3f0be3f8e498ee2edcd0d1a033060'
NESSUS_SECRET_KEY = 'a4f1a47d7dddf2b2d48740472ba04facbae990e32263892c530fcae01e93a475'
