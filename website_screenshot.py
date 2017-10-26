""" From list of webservers create a screenshot of each website """
import os
import time
import logging
import argparse
from io import BytesIO
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from PIL import Image
from pyvirtualdisplay import Display  # pylint: disable=import-error
from selenium import webdriver  # pylint: disable=import-error
from selenium.common.exceptions import TimeoutException, WebDriverException  # pylint: disable=import-error
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # pylint: disable=import-error

import config
import utils
import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.website_screenshot")


def take_screenshot(url, output_dir, url_list=None, proxy=False):  # noqa pylint: disable=too-many-locals,too-many-statements,too-many-return-statements
    LOG.info("Taking a screenshot of {}".format(url))
    display = Display(visible=0, size=(1200, 1800))
    display.start()

    fc = DesiredCapabilities.FIREFOX
    fc['handleAlerts'] = True
    fc['acceptSslCerts'] = True
    fc['acceptInsecureCerts'] = True
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    gd_path = os.path.join(config.SCRIPTS_PATH, 'geckodriver')
    driver = webdriver.Firefox(
        firefox_profile=profile, capabilities=fc, executable_path=gd_path)
    driver.set_page_load_timeout(10)
    LOG.info('Selenium is connecting to {}'.format(url))

    # Get the page
    try:
        driver.get(url)
    except TimeoutException:
        LOG.info("Selenium timeout occured, moving on.")
        driver.close()
        display.stop()
        return
    except WebDriverException:
        LOG.info("Selenium WebDriverException, moving on.")
        driver.close()
        display.stop()
        return

    # Check for redirections
    end_url = driver.current_url
    if not end_url == url:
        # If we are redirected, check if current url is in list of urls to check
        # If it is then no need to take a picture.
        if end_url in url_list:
            LOG.info('redirected to {} going to look at it later'.format(end_url))
            return
        else:
            LOG.info('redirected from {} to {}'.format(url, end_url))
            if end_url == 'about:blank':
                return
    url_parsed = urlparse(url)
    domain = url_parsed.netloc.split(':')[0]
    port = url_parsed.port
    if port is None and url_parsed.scheme == 'http':
        port = '80'
    elif port is None and url_parsed.scheme == 'https':
        port = '443'
    if proxy:
        # give it a bit more time if using proxy
        LOG.info('Sleeping for {} seconds before taking screenshot.'.format(config.PROXY_SLEEP))
        time.sleep(config.PROXY_SLEEP)
    file_name = os.path.join(output_dir, '{}_{}.jpg'.format(domain, port))
    LOG.info('Taking screenshot and saving it to {}'.format(file_name))

    # We are going to save it as jpg to get rid of the transparency of png
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    rgb_im = im.convert('RGB')
    rgb_im.save(file_name)
    driver.close()
    display.stop()


def run_website_screenshot(url_file, output_dir, proxy):
    utils.dir_exists(output_dir, True)
    urls = utils.parse_webserver_urls(url_file)
    for url in urls:
        if utils.check_url(url):
            take_screenshot(url, output_dir, urls, proxy)


def parse_args():
    parser = argparse.ArgumentParser(description='Read file of urls and then take a screenshot of each.')
    parser.add_argument('input_file', help='a file with a line for each webserver')
    parser.add_argument('output_dir', help='directory to write images to')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    run_website_screenshot(parse_args().input_file, parse_args().output_dir, parse_args().proxy)
