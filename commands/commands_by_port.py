""" Commands to run when a specific port is found by nmap. """
commands = {
    "21": {
        "header": "FTP Commands",
        "commands": [
            "hydra -L /usr/share/wordlists/metasploit/unix_users.txt -P /usr/share/wordlists/rockyou.txt -v {ip} ftp",
            "Another ftp command",
        ]
    },
}
