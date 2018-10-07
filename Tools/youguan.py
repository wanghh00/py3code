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

from utils import comm
from utils import webdriverbuilder

comm.initLOG()
LstUrl, LstProxy = [], []

GITPROXFILE_URL = 'https://raw.githubusercontent.com/wanghh00/py3code/master/Tools/proxyfile'
# 'ETag': '"9f6b65f8d9d46b1f92b3ae982d878a4ca92a7537"' could be used to identify change of file

class Player(object):
    def __init__(self, driverBuilder):
        self.driverBuilder = driverBuilder
        self.sanityLocator = "logo-icon-container"
        self.waitSanityLocator = 60
        self.adLocator = "player-ads"
        self.waitAdLocator = 60
        self.clickAd = False
        self.seeAd = 60
    
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
            rint = random.randint(1,10)
            LOG.info("RandInt: %s" % rint)
            if locator and self.clickAd and rint == 10:
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
                    time.sleep(self.seeAd)

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

fireFoxDriverBuilder = webdriverbuilder.FireFoxDriverBuilder()
chromeDriverBuilder = webdriverbuilder.ChromeDriverBuilder()

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
        fd = comm.getFileDesc(pathLinkFile)
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
        fd = comm.getFileDesc(pathProxyFile)
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
