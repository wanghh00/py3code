#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse
import requests

import os
import time, sys, re, random
import logging; LOG = logging.getLogger(__name__)

LOGFMT = '[%(asctime)s %(filename)s:%(lineno)d] %(message)s'
LOGDATEFMT = '%Y%m%d-%H:%M:%S'

DctFileDesc = {}
LstUrl, LstProxy = [], []

class DriverBuilder(object):
    def __init__(self, proxy=''):
        self.proxy = proxy
        self.dryrun = False
    
    def setProxy(self, proxy):
        self.proxy = proxy
        return self
    
    def setDryrun(self, dryrun):
        self.dryrun = dryrun
        return self

    def _getDriver(self):
        raise NotImplementedError

    def getDriver(self):
        ret = None
        if self.dryrun:
            return ret
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

def waitPlay(driver, url, minutes, locator="", waitlocator=60):
    if not driver:
        return

    try:
        LOG.info("Playing url=%s minutes=%s" % (url, minutes))
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

def chkProxy(proxy):
    ret = True
    response = None
    if proxy:
        try:
            response = requests.get("https://example.com/", proxies={'https':proxy}, timeout=(9.05, 27))
            ret = response.status_code == 200
        except Exception:
            ret = False
        finally:
            response and response.close()
        LOG.info("Check proxy: %s [%s]" % (proxy, ret))
    return ret

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--linkfile', help='File include link and minutes in one line')
    parser.add_argument('-p', '--proxyfile', help='File include proxy and port each line')
    parser.add_argument('-n', '--numberoftimes', help='Number of times to run', type=int, default=1)
    parser.add_argument('-b', '--browsers', help='Browsers to be used', default='chrome')
    parser.add_argument('--dryrun', action='store_true')

    return parser.parse_args()

def getFileDesc(path):
    try:
        if not path:
            return None
        fd = None
        info = os.stat(path)
        if path not in DctFileDesc:
            DctFileDesc[path] = 0
        if DctFileDesc[path] == int(info.st_mtime):
            return None
        LOG.info("Loading %s" % path)
        fd = open(path)
        DctFileDesc[path] = int(info.st_mtime)
    except Exception as ex:
        LOG.error(ex)
        fd = None
    return fd

logging.basicConfig(format=LOGFMT,datefmt=LOGDATEFMT)
logging.getLogger().setLevel(logging.INFO)

fireFoxDriverBuilder = FireFoxDriverBuilder()
chromeDriverBuilder = ChromeDriverBuilder()

args = parseArguments()
#print(args.linkfile)
#print(args.proxyfile)

lstBrowsers = args.browsers.split(',')

def getLstUrl(pathLinkFile):
    global LstUrl
    try:
        fd = getFileDesc(pathLinkFile)
        if not fd:
            return LstUrl
        LstUrl = []
        for one in fd:
            one = one.strip()
            if not one or one[0] == '#': continue
            url, duration = re.split(r'\s+', one)
            LstUrl.append((url, int(duration)))
    finally:
        fd and fd.close()
    random.shuffle(LstUrl)
    return LstUrl

def getProxyUrl(pathProxyFile):
    global LstProxy
    fd = None
    try:
        fd = getFileDesc(pathProxyFile)
        if not fd:
            LstProxy = LstProxy or [""]*args.numberoftimes
            return LstProxy 
        LstProxy = []
        for one in fd:
            one = one.strip()
            if not one or one[0] == '#': continue
            LstProxy.extend([one]*args.numberoftimes)
    finally:
        fd and fd.close()
    random.shuffle(LstProxy)
    return LstProxy

while 1:
    for proxy in getProxyUrl(args.proxyfile):
        LOG.info("Using Proxy [%s]" % proxy)

        if not chkProxy(proxy):
            continue
        
        for one in getLstUrl(args.linkfile):
            browser = random.choice(lstBrowsers).lower()
            builder = chromeDriverBuilder
            if browser == 'firefox':
                builder = fireFoxDriverBuilder
            
            driver = builder.setProxy(proxy).setDryrun(args.dryrun).getDriver()
            waitPlay(driver, one[0], one[1], "logo-icon-container")
