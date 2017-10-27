import os
import yaml

import config


def get_input():
    pentest_name = input('Pentest directory name? ')  # noqa: F821
    domain_name = input('Domain for dnsrecon? ')  # noqa: F821
    ip_file = input('Name of ip file [ips.txt]: ') or "ips.txt"  # noqa: F821
    return {'pentest_name': pentest_name,
            'domain_name': domain_name,
            'ip_file': ip_file}


def c_format(commands, params):
    for com in commands:
        com['command'] = com['command'].format(
            scripts_path=config.SCRIPTS_PATH,
            pentest_path=os.path.join(config.BASE_PATH, params['pentest_name']),
            ip_file=params['ip_file'],
            pentest_name=params['pentest_name'],
        )


def c_print(commands):
    for com in commands:
        if com.get('help') and com['help']:
            print('# ' + com['help'])
        print(com['command'])


def load_commands(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


def main():
    params = get_input()
    commands = load_commands("commands.yaml")
    c_format(commands, params)
    c_print(commands)


if __name__ == "__main__":
    main()
