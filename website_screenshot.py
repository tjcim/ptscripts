""" From list of webservers create a screenshot of each website """
import os
import argparse
from io import BytesIO
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from PIL import Image
from selenium import webdriver  # pylint: disable=import-error

from utils import parse_webserver_urls, dir_exists


def take_screenshot(url, output_dir, url_list=None):
    driver = webdriver.PhantomJS(service_args=[
        '--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false'])
    driver.set_window_size(1024, 768)  # set the window size that you need
    if not url.endswith('/'):
        url = url + '/'
    driver.get(url)
    end_url = driver.current_url
    if end_url == url:
        print('not redirected')
    else:
        # If we are redirected, check if current url is in list of urls to check
        # If it is then no need to take a picture.
        if end_url in url_list:
            print('redirected but going to look at it later')
            return
        else:
            print('redirected from {} to {}'.format(url, end_url))
    url_parsed = urlparse(url)
    domain = url_parsed.netloc.split(':')[0]
    port = url_parsed.port
    if port is None and url_parsed.scheme == 'http':
        port = '80'
    elif port is None and url_parsed.scheme == 'https':
        port = '443'
    file_name = os.path.join(output_dir, '{}_{}.jpg'.format(domain, port))
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    rgb_im = im.convert('RGB')
    rgb_im.save(file_name)


def run_website_screenshot(url_file, output_dir):
    dir_exists(output_dir, True)
    urls = parse_webserver_urls(url_file)
    for url in urls:
        take_screenshot(url, output_dir, urls)


def parse_args():
    parser = argparse.ArgumentParser(description='Read file of urls and then take a screenshot of each.')
    parser.add_argument('input_file', help='a file with a line for each webserver')
    parser.add_argument('output_dir', help='directory to write images to')
    return parser.parse_args()


if __name__ == '__main__':
    run_website_screenshot(parse_args().input_file, parse_args().output_dir)
