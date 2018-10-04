#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pyautogui, platform
import argparse
import requests

import os
import time, sys, re, random
import logging; LOG = logging.getLogger(__name__)

LOGFMT = '[%(asctime)s %(filename)s:%(lineno)d] %(message)s'
LOGDATEFMT = '%Y%m%d-%H:%M:%S'

DctFileDesc = {}
LstUrl, LstProxy = [], []

GITPROXFILE_URL = 'https://raw.githubusercontent.com/wanghh00/py3code/master/Tools/proxyfile'
# 'ETag': '"9f6b65f8d9d46b1f92b3ae982d878a4ca92a7537"' could be used to identify change of file

class DriverBuilder(object):
    def __init__(self, proxy=''):
        self.proxy = proxy
        self.dryrun = False
        self.start_x = 0
        self.start_y = 0
        self.width = 1100
        self.height = 768
        self.browserHeaderHeight = 150
        self.extraHeader = 30 if platform.system() == 'Darwin' else 0
    
    def setProxy(self, proxy):
        self.proxy = proxy
        return self
    
    def setDimension(self, width, height):
        self.width = int(width)
        self.height = int(height)
        return self

    def setLocation(self, x0, y0, x1=0, y1=0):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        self.start_x = x0
        self.start_y = y0

        if x1 > x0 and y1 > y0:
            self.width = abs(x1 - x0)
            self.height = abs(y1 - y0)
        return self
    
    def setBrowserHeaderHeight(self, headerHeight):
        self.browserHeaderHeight = headerHeight
        return self

    def setDryrun(self, dryrun):
        self.dryrun = dryrun
        return self

    def _getDriver(self):
        raise NotImplementedError

    def getDriver(self):
        driver = None
        LOG.info("Launch browser with proxy: %s" % self.proxy)
        if self.dryrun:
            return driver
        try:
            driver = self._getDriver()
            driver.set_window_size(self.width, self.height)
            driver.set_window_position(self.start_x, self.start_y)
        except Exception as ex:
            LOG.exception(ex)
        return driver

class FireFoxDriverBuilder(DriverBuilder):
    def __init__(self, proxy=''):
        DriverBuilder.__init__(self, proxy)
    
    def _getDriver(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.link.open_newwindow", 1)

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


class Player(object):
    def __init__(self, driverBuilder):
        self.driverBuilder = driverBuilder
        self.sanityLocator = "logo-icon-container"
        self.waitSanityLocator = 60
        self.adLocator = "player-ads"
        self.waitAdLocator = 60
        self.clickAd = False
    
    def setSanityLocator(self, sanityLocator, waitSanityLocator = 60):
        self.sanityLocator = sanityLocator
        self.waitSanityLocator = waitSanityLocator
        return self
    
    def setAdLocator(self, adLocator, waitAdLocator = 30):
        self.adLocator = adLocator
        self.waitAdLocator = waitAdLocator
        return self
    
    def setClickAd(self, clickAd):
        self.clickAd = clickAd
        return self

    #def waitPlay(self, url, minutes, locator="", waitlocator=60):
    def play(self, url, minutes):
        self.driver = self.driverBuilder.getDriver()

        if not self.driver:
            return

        try:
            LOG.info("Playing url=%s minutes=%s" % (url, minutes))
            self.driver.get(url)

            locator, waitlocator = self.sanityLocator, self.waitSanityLocator
            if locator:
                LOG.info("Checking Page loading")
                WebDriverWait(self.driver, waitlocator).until(
                    EC.presence_of_element_located((By.ID, locator)))
                LOG.info('Page loaded')
            
            locator, waitlocator = self.adLocator, self.waitAdLocator
            if locator and self.clickAd:
                start = time.time()
                adShowed = False
                while (time.time() - start) < waitlocator:
                    LOG.info("Checking AD loading")
                    WebDriverWait(self.driver, waitlocator).until(
                        EC.presence_of_element_located((By.ID, locator)))
                    #LOG.info("AD loaded")
                    time.sleep(5)
                    
                    elemAd = self.driver.find_element(By.ID, locator)
                    elemAdPos = elemAd.location
                    elemAdSize = elemAd.size
                    LOG.info('AD element location: ' + str(elemAdPos))
                    LOG.info('AD element size: ' + str(elemAdSize))

                    if elemAdSize['height'] > 10:
                        adShowed = True
                        break
                
                if adShowed:
                    builder = self.driverBuilder

                    x = builder.start_x + builder.width - 1 # to avoid the icon
                    y = builder.start_y + 1 + builder.extraHeader # mac header
                    LOG.info("Click browser at x:%s y:%s" % (x, y))
                    pyautogui.click(x, y, clicks=2, interval=0.5)
                    time.sleep(3)

                    x = builder.start_x + elemAdPos['x'] + 50
                    y = builder.start_y + elemAdPos['y'] + builder.browserHeaderHeight + 20
                    LOG.info("Click AD at x:%s y:%s" % (x, y))
                    pyautogui.click(x, y)
                    time.sleep(10)

                    LOG.info("Check new tab")
                    if len(self.driver.window_handles) > 1:
                        LOG.info("Close the new Tab")
                        self.driver.switch_to_window(self.driver.window_handles[1])
                        self.driver.close()

            LOG.info('Begin to play')
            for x in range(minutes):
                time.sleep(60)
                LOG.info("Played %s mintues" % x)
        except Exception as ex:
            LOG.exception(ex)
        finally:
            self.driver.quit()

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
    parser.add_argument('-l', '--location', help='Browse location x0,y0,x1,y1')
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('--clickad', action='store_true')

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

if args.location:
    locs = args.location.split(',')
    fireFoxDriverBuilder.setLocation(*locs)
    chromeDriverBuilder.setLocation(*locs)

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
    for one in  getLstUrl(args.linkfile):

        proxyList = getProxyUrl(args.proxyfile)
        while 1:
            proxy = random.choice(proxyList)
            if chkProxy(proxy):
                break
        
        browser = random.choice(lstBrowsers).lower()
        builder = chromeDriverBuilder
        if browser == 'firefox':
            builder = fireFoxDriverBuilder
        
        #driver = builder.setProxy(proxy).setDryrun(args.dryrun).getDriver()
        #waitPlay(driver, one[0], one[1], "logo-icon-container")
        builder.setProxy(proxy).setDryrun(args.dryrun)
        Player(builder).setClickAd(args.clickad).play(one[0], one[1])
