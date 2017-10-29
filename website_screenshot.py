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

from config import config
from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.website_screenshot")


def get_driver():
    fc = DesiredCapabilities.FIREFOX
    fc['handleAlerts'] = True
    fc['acceptSslCerts'] = True
    fc['acceptInsecureCerts'] = True
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    gd_path = os.path.join(config.SCRIPTS_PATH, 'utils/geckodriver')
    driver = webdriver.Firefox(
        firefox_profile=profile, capabilities=fc, executable_path=gd_path)
    driver.set_page_load_timeout(10)
    return driver


def get_filename(output_dir, url):
    url_parsed = urlparse(url)
    domain = url_parsed.netloc.split(':')[0]
    port = url_parsed.port
    if port is None and url_parsed.scheme == 'http':
        port = '80'
    elif port is None and url_parsed.scheme == 'https':
        port = '443'
    return os.path.join(output_dir, '{}_{}.jpg'.format(domain, port))


def take_screenshot(url, output_dir, url_list=None, proxy=False):
    LOG.info("Taking a screenshot of {}".format(url))
    display = Display(visible=0, size=(1200, 1800))
    display.start()
    driver = get_driver()
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
    if proxy:
        # give it a bit more time if using proxy
        LOG.info('Sleeping for {} seconds before taking screenshot.'.format(config.PROXY_SLEEP))
        time.sleep(config.PROXY_SLEEP)

    file_name = get_filename(output_dir, url)
    LOG.info('Taking screenshot and saving it to {}'.format(file_name))

    # We are going to save it as jpg to get rid of the transparency of png
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    rgb_im = im.convert('RGB')
    rgb_im.save(file_name)
    driver.close()
    display.stop()


def main(args):
    utils.dir_exists(args.output_dir, True)
    urls = utils.parse_webserver_urls(args.input_file)
    for url in urls:
        if utils.check_url(url):
            take_screenshot(url, args.output_dir, urls, args.proxy)


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Read file of urls and then take a screenshot of each.',
        prog='website_screenshot.py',
    )
    parser.add_argument('input_file', help='a file with a line for each webserver')
    parser.add_argument('output_dir', help='directory to write images to')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        LOG.debug("Logging set to debug.")
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
