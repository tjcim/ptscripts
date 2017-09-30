""" Build a file to test iframe """
import os
import argparse


def write_iframe(url, output_dir):
    iframe_html = """
    <html>
    <head>
    </head>
    <body>
    <h1>Website {0} inside iFrame</h1>
    <iframe src="{0}" height=600 width=600>
    </body>
    </html>
    """.format(url)
    output_file = os.path.join(output_dir, 'iframe.html')

    with open(output_file, 'wb') as f:
        f.write(iframe_html)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('website')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    website = os.path.expanduser(args.website)
    output_dir = os.path.expanduser(args.output_dir)
    return(website, output_dir)


if __name__ == '__main__':
    website, output_dir = parse_args()
    write_iframe(website, output_dir)
