""" Build a file to test iframe """
import os
import sys
import argparse


def write_iframe(args):
    iframe_html = """
    <html>
    <head>
    </head>
    <body>
    <h1>Website {0} inside an iFrame</h1>
    <iframe src="{0}" height=600 width=600>
    </body>
    </html>
    """.format(args.website)
    output_file = os.path.join(args.output_dir, 'iframe.html')

    with open(output_file, 'w') as f:
        f.write(iframe_html)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('website')
    parser.add_argument('output_dir')
    return parser.parse_args(args)


if __name__ == '__main__':
    write_iframe(parse_args(sys.argv[1:]))
