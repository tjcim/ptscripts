import os
import logging
import subprocess

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.run_commands")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def bash_command(command, split=True):
    """ Runs the command with bash - prints the results as it happens as well as returning the
    output of the command as a string when complete."""
    if split:
        command = command.split()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    full = []
    for line in iter(proc.stdout.readline, b''):
        line = line.rstrip().decode('utf-8')
        print(line)
        full.append(line)
    return '\n'.join(full)


def create_html_file(command_output, command, html_file_path, max_lines=300):  # python: disable=too-many-locals
    """ Creates an html file using aha with the contents of output (limits to max_lines) """
    command_output = command_output.encode('utf-8')
    full = []
    proc = subprocess.Popen(["aha", "--no-header"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cmd_results = proc.communicate(input=command_output)[0].decode('utf-8')
    for line in cmd_results.splitlines():
        line = line.rstrip()
        full.append(line)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('bash_output_template.html.j2')
    head, ext = os.path.splitext(html_file_path)
    full_html_file_path = head + "_full" + ext
    full_output = "\n".join(full)
    output = "\n".join(full[:max_lines])
    full_html_content = template.render(output=full_output, command=command)
    with open(full_html_file_path, 'w') as f:
        f.write(full_html_content)
    html_content = template.render(output=output, command=command)  # pylint: disable=no-member
    with open(html_file_path, 'w') as f:
        f.write(html_content)

    return full_html_file_path
