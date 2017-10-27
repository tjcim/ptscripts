"""
Take images of the results from dnsdumpster

USAGE: python dnsdumpster_images.py <output_dir> <domain>

TODO:
    Better debug logging
    Error handling for both selenium and requests
"""
import os
import logging
import argparse

from requests import get
from selenium import webdriver  # pylint: disable=import-error
from selenium.webdriver.common.by import By  # pylint: disable=import-error
from selenium.webdriver.support.ui import WebDriverWait  # pylint: disable=import-error
from selenium.webdriver.support import expected_conditions as EC  # pylint: disable=import-error
from selenium.common.exceptions import TimeoutException, WebDriverException  # pylint: disable=import-error
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # pylint: disable=import-error

from ptscripts import utils
from ptscripts import config
from ptscripts import logging_config  # noqa pylint: disable=unused-import


LOG = logging.getLogger("ptscripts.dnsdumpster_images")


def selenium_open_dnsdumpster():
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

    # Get the page
    try:
        driver.get("https://dnsdumpster.com/")
    except TimeoutException:
        LOG.info("Selenium timeout occured, moving on.")
        driver.close()
        return
    except WebDriverException:
        LOG.info("Selenium WebDriverException, moving on.")
        driver.close()
        return

    return driver


def fill_in_form(driver, domain):
    element = driver.find_element(By.NAME, "targetip")
    element.send_keys(domain)
    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit.click()


def take_screenshot(output_dir, domain, driver):
    utils.dir_exists(output_dir, True)
    filename = "dnsdumpster_{}.png".format(domain)
    screenshot_path = os.path.join(output_dir, filename)

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@name='dnsanchor']"))
    )
    # driver.execute_script("return arguments[0].scrollIntoView();", element)
    driver.save_screenshot(screenshot_path)


def get_domain_map(output_dir, domain):
    output_file = os.path.join(output_dir, "dnsdumpster_{}_map.png".format(domain))
    response = get("https://dnsdumpster.com/static/map/{}.png".format(domain))
    with open(output_file, "wb") as f:
        f.write(response.content)


def main(args):
    LOG.info("Opening dnsdumpster with selenium.")
    driver = selenium_open_dnsdumpster()
    if not driver:
        LOG.error("Selenium couldn't open dnsdumpster.")
        raise SystemExit
    LOG.info("Submitting the domain {}".format(args.domain))
    fill_in_form(driver, args.domain)
    LOG.info("Taking the screenshot.")
    take_screenshot(args.output, args.domain, driver)
    LOG.info("Grabbing the map.")
    get_domain_map(args.output, args.domain)
    driver.close()


def parse_args(args):
    parser = argparse.ArgumentParser(
        parents=[utils.parent_argparser()],
        description='Capture DNSDumpster Images',
    )
    parser.add_argument('output', help="full path to where the images will be saved.")
    parser.add_argument('domain', help="Domain to capture.")
    args = parser.parse_args(args)
    logger = logging.getLogger("ptscripts")
    if args.quiet:
        logger.setLevel('ERROR')
    elif args.verbose:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')
    return args


if __name__ == "__main__":
    import sys
    main(parse_args(sys.argv[1:]))
