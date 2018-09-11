#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse

import time, sys, re, random
import logging; LOG = logging.getLogger(__name__)

LOGFMT = '[%(asctime)s %(filename)s:%(lineno)d] %(message)s'
LOGDATEFMT = '%Y%m%d-%H:%M:%S'

class DriverBuilder(object):
    def __init__(self, proxy=''):
        self.proxy = proxy
    
    def setProxy(self, proxy):
        self.proxy = proxy
        return self
    
    def _getDriver(self):
        raise NotImplementedError

    def getDriver(self):
        ret = None
        try:
            ret = self._getDriver()
        except Exception as ex:
            LOG.exception(ex)
        return ret

class FireFoxDriverBuilder(DriverBuilder):
    def __init__(self, proxy=''):
        DriverBuilder.__init__(self, proxy)
    
    def _getDriver(self):
        profile = webdriver.FirefoxProfile()
        if self.proxy:
            host, port = self.proxy.split(":")
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", host)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference("network.proxy.ssl", host)
            profile.set_preference("network.proxy.ssl_port", port)

        return webdriver.Firefox(firefox_profile=profile)

class ChromeDriverBuilder(DriverBuilder):
    def __init__(self, proxy=''):
        DriverBuilder.__init__(self, proxy)
        self.arguments = ['--ignore-certificate-errors']
    
    def setArguments(self, arguments):
        self.arguments = arguments
        return self

    def _getDriver(self):
        #options = webdriver.ChromeOptions()
        #options.add_argument('--ignore-certificate-errors')
        #options.add_argument("--test-type")
        #options.binary_location = "/Users/hongwang/Bin/chromium"
        #options.add_argument("user-data-dir=" + profilePath)
        #options.add_argument("headless")
        #options.add_argument('window-size=1920x1080')
        #options.add_argument('--proxy-server=%s' % PROXY)

        options = webdriver.ChromeOptions()
        for arg in self.arguments:
            options.add_argument(arg)
        
        if self.proxy:
            options.add_argument('--proxy-server=%s' % self.proxy)
        
        return webdriver.Chrome(chrome_options=options)

def waitPlay(driver, url, minutes, locator="", waitlocator=60, dryrun=False):
    LOG.info("Playing url=%s minutes=%s" % (url, minutes))

    if dryrun:
        driver.quit()
        return

    try:
        driver.get(url)
        if locator:
            LOG.info("Checking Page loaded")
            WebDriverWait(driver, waitlocator).until(
                EC.presence_of_element_located((By.ID, locator)))

        for x in range(minutes):
            time.sleep(60)
            LOG.info("Played %s mintues" % x)
    except Exception as ex:
        LOG.exception(ex)
    finally:
        driver.quit()

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--linkfile', help='File include link and minutes in one line')
    parser.add_argument('-p', '--proxyfile', help='File include proxy and port each line')
    parser.add_argument('-n', '--numberoftimes', help='Number of times to run', type=int, default=1)
    parser.add_argument('-b', '--browsers', help='Browsers to be used', default='chrome')

    return parser.parse_args()

logging.basicConfig(format=LOGFMT,datefmt=LOGDATEFMT)
logging.getLogger().setLevel(logging.INFO)

fireFoxDriverBuilder = FireFoxDriverBuilder()
chromeDriverBuilder = ChromeDriverBuilder()

args = parseArguments()
#print(args.linkfile)
#print(args.proxyfile)

lstBrowsers = args.browsers.split(',')

lstUrl = []
if args.linkfile:
    with open(args.linkfile) as fd:
        for one in fd:
            one = one.strip()
            if not one or one[0] == '#': continue
            url, duration = re.split(r'\s+', one)
            lstUrl.append((url, int(duration)))
else:
    lstUrl.append(('https://www.youtube.com/watch?v=9LET0ZM7qXg',30))

lstProxy = []
if args.proxyfile:
    with open(args.proxyfile) as fd:
        for one in fd:
            one = one.strip()
            if not one or one[0] == '#': continue
            lstProxy.extend([one]*args.numberoftimes)
else:
    lstProxy.extend([""]*args.numberoftimes)

#lstArgs = ['--ignore-certificate-errors']
random.shuffle(lstProxy)
for proxy in lstProxy:
    LOG.info("Using Proxy [%s]" % proxy)
    for one in lstUrl:
        browser = random.choice(lstBrowsers).lower()
        builder = chromeDriverBuilder
        if browser == 'firefox':
            builder = fireFoxDriverBuilder
        
        LOG.info(proxy)
        driver = builder.setProxy(proxy).getDriver()
        waitPlay(driver, one[0], one[1], "logo-icon-container")
