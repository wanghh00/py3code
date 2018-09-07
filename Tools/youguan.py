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

def getChromeDriver(arguments=[], proxy=""):
    #options = webdriver.ChromeOptions()
    #options.add_argument('--ignore-certificate-errors')
    #options.add_argument("--test-type")
    #options.binary_location = "/Users/hongwang/Bin/chromium"
    #options.add_argument("user-data-dir=" + profilePath)
    #options.add_argument("headless")
    #options.add_argument('window-size=1920x1080')
    #options.add_argument('--proxy-server=%s' % PROXY)

    options = webdriver.ChromeOptions()
    for arg in arguments:
        options.add_argument(arg)
    
    if proxy:
        options.add_argument('--proxy-server=%s' % proxy)
    
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
                EC.presence_of_element_located((By.ID, "logo-icon-container")))

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
    parser.add_argument('-n', '--numberoftimes', help='number of times to run', type=int, default=1)

    return parser.parse_args()

logging.basicConfig(format=LOGFMT,datefmt=LOGDATEFMT)
logging.getLogger().setLevel(logging.INFO)

args = parseArguments()
#print(args.linkfile)
#print(args.proxyfile)

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
    lstProxy.append([""]*args.numberoftimes)

lstArgs = ['--ignore-certificate-errors']
random.shuffle(lstProxy)
for proxy in lstProxy:
    LOG.info("Using Proxy [%s]" % proxy)
    for one in lstUrl:
        driver = getChromeDriver(lstArgs, proxy)
        waitPlay(driver, one[0], one[1], "logo-icon-container")
