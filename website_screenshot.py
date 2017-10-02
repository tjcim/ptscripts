""" From list of webservers create a screenshot of each website """
import os
import time
import argparse
from io import BytesIO
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from PIL import Image
from selenium import webdriver  # pylint: disable=import-error
from selenium.common.exceptions import TimeoutException  # pylint: disable=import-error

import config
from utils import parse_webserver_urls, dir_exists


def take_screenshot(url, output_dir, url_list=None, proxy=False):
    service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false']
    if proxy:
        service_args.append('--proxy=127.0.0.1:{}'.format(config.PROXY_PORT))
        service_args.append('--proxy-type=socks5')
    print('Connecting to {}'.format(url))
    driver = webdriver.PhantomJS(service_args=service_args)

    # Set Timeouts
    print('timeouts')
    driver.implicitly_wait(config.PROXY_SLEEP)
    driver.set_page_load_timeout(config.PROXY_SLEEP)

    # Set browser size
    print('size')
    driver.set_window_size(1024, 768)  # set the window size that you need

    # Get the page
    try:
        print('get')
        driver.get(url)
    except TimeoutException:
        print('    Timeout occurred moving on')
        driver.quit()
        return

    # Check for redirections
    end_url = driver.current_url
    if not end_url == url:
        # If we are redirected, check if current url is in list of urls to check
        # If it is then no need to take a picture.
        if end_url in url_list:
            print('    redirected to {} going to look at it later'.format(end_url))
            return
        else:
            print('    redirected from {} to {}'.format(url, end_url))
    url_parsed = urlparse(url)
    domain = url_parsed.netloc.split(':')[0]
    port = url_parsed.port
    if port is None and url_parsed.scheme == 'http':
        port = '80'
    elif port is None and url_parsed.scheme == 'https':
        port = '443'
    if proxy:
        # give it a bit more time if using proxy
        print('    Sleeping for {} seconds before taking screenshot.'.format(config.PROXY_SLEEP))
        time.sleep(config.PROXY_SLEEP)
    file_name = os.path.join(output_dir, '{}_{}.jpg'.format(domain, port))
    print('    Taking screenshot and saving it to {}'.format(file_name))

    # We are going to save it as jpg to get rid of the transparency of png
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    rgb_im = im.convert('RGB')
    rgb_im.save(file_name)
    driver.quit()


def run_website_screenshot(url_file, output_dir, proxy):
    dir_exists(output_dir, True)
    urls = parse_webserver_urls(url_file)
    for url in urls:
        take_screenshot(url, output_dir, urls, proxy)


def parse_args():
    parser = argparse.ArgumentParser(description='Read file of urls and then take a screenshot of each.')
    parser.add_argument('input_file', help='a file with a line for each webserver')
    parser.add_argument('output_dir', help='directory to write images to')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    run_website_screenshot(parse_args().input_file, parse_args().output_dir, parse_args().proxy)
