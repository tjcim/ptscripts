""" From list of webservers create a screenshot of each website """
import os
import time
import logging
import argparse
import threading
from io import BytesIO
from queue import Queue
from urllib.parse import urlparse  # pylint: disable=no-name-in-module, import-error

from PIL import Image
from pyvirtualdisplay import Display  # pylint: disable=import-error
from selenium import webdriver  # pylint: disable=import-error
from selenium.common.exceptions import TimeoutException, WebDriverException  # pylint: disable=import-error
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # pylint: disable=import-error
# from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import config
from utils import utils
from utils import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.website_screenshot")
LOG_LOCK = threading.Lock()


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


def take_screenshot(url, url_list, args):  # noqa
    def close_and_return():
        driver.close()
        if not args.no_display:
            display.stop()

    with LOG_LOCK:
        LOG.info("Taking a screenshot of {}".format(url))
    if not args.no_display:
        display = Display(visible=0, size=(1200, 1800))
        display.start()
    driver = get_driver()
    with LOG_LOCK:
        LOG.info('Selenium is connecting to {}'.format(url))

    # Get the page
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(), 'Timed out waiting alret.')
            alert = driver.switch_to.alert
            alert.accept()
            with LOG_LOCK:
                LOG.info("alert accepted {}".format(url))
        except TimeoutException:
            with LOG_LOCK:
                LOG.info("no alert continuing on")
    except TimeoutException:
        with LOG_LOCK:
            LOG.info("Selenium timeout occured, moving on.")
        close_and_return()
        return
    except WebDriverException:
        with LOG_LOCK:
            LOG.info("Selenium WebDriverException, moving on.")
        close_and_return()
        return

    # Check for redirections
    end_url = driver.current_url
    if not end_url == url:
        # If we are redirected, check if current url is in list of urls to check
        # If it is then no need to take a picture.
        if end_url in url_list:
            with LOG_LOCK:
                LOG.info('redirected to {} going to look at it later'.format(end_url))
            close_and_return()
            return
        with LOG_LOCK:
            LOG.info('redirected from {} to {}'.format(url, end_url))
        if end_url == 'about:blank':
            close_and_return()
            return

    file_name = get_filename(args.output_dir, url)
    with LOG_LOCK:
        LOG.info('Taking screenshot and saving it to {}'.format(file_name))

    # We are going to save it as jpg to get rid of the transparency of png
    time.sleep(2)  # wait an extra 2 seconds before taking image
    screen = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen))
    rgb_im = im.convert('RGB')
    rgb_im.save(file_name)
    close_and_return()


def process_queue(args, url_queue, imaged_urls, urls):
    while True:
        url = url_queue.get()
        if not args.force:
            file_name = get_filename(args.output_dir, url)
            if os.path.isfile(file_name):
                with LOG_LOCK:
                    LOG.info(
                        "Skipping {url} as it has already been done (use -f to force).".format(url=url)
                    )
                url_queue.task_done()
                continue

        # Use requests to check that the URL is valid (requests is much faster).
        valid, end_url = utils.check_url(url)
        with LOG_LOCK:
            LOG.debug("check_url results: {}, {}".format(valid, end_url))
        if end_url in imaged_urls:
            with LOG_LOCK:
                LOG.info("Skipping, already took an image of this end_url {}".format(end_url))
            url_queue.task_done()
            continue

        # Check if redirected and then if the end_url is in urls
        parsed_url = urlparse(end_url)
        if parsed_url.scheme == 'https' and parsed_url.port == 443:
            # remove port
            end_url = 'https://' + parsed_url.netloc.split(":")[0] + parsed_url.path
        elif parsed_url.scheme == 'http' and parsed_url.port == 80:
            # remove port
            end_url = 'http://' + parsed_url.netloc.split(":")[0] + parsed_url.path
        if not end_url == url:
            if end_url in urls:
                with LOG_LOCK:
                    LOG.info("Skipping, redirected to a url later in the list: {}".format(end_url))
                url_queue.task_done()
                continue

        # If url is valid, take the screenshot and then add end_url to imaged_urls list
        if valid:
            take_screenshot(url, urls, args)
            imaged_urls.append(end_url)
        url_queue.task_done()


def main(args):
    imaged_urls = []
    utils.dir_exists(args.output_dir, True)
    urls = utils.parse_webserver_urls(args.input_file)
    url_queue = Queue()

    for _ in range(args.threads):
        t = threading.Thread(
            target=process_queue,
            kwargs={
                'args': args,
                'url_queue': url_queue,
                'imaged_urls': imaged_urls,
                'urls': urls,
            }
        )
        t.daemon = True
        t.start()

    for current_url in urls:
        url_queue.put(current_url)

    url_queue.join()


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Read file of urls and then take a screenshot of each.',
        prog='website_screenshot.py',
    )
    parser.add_argument('input_file', help='a file with a line for each webserver')
    parser.add_argument('output_dir', help='directory to write images to')
    parser.add_argument('--proxy', help='Use proxychains', action='store_true')
    parser.add_argument('-n', '--no-display', help="Don't use virtual display",
                        action='store_true', default=False)
    parser.add_argument('-f', '--force', help="Don't resume, start over.", action="store_true")
    parser.add_argument('-t', '--threads', help="Number of threads (default is 2).",
                        default=2, type=int)
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
        with LOG_LOCK:
            LOG.debug("Logging set to debug.")
    else:
        logger.setLevel('INFO')
    return args


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
