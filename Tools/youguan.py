#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse

import time, sys, re, random

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

def waitPlay(driver, url, minutes, locator="", waitlocator=30, dryrun=False):
    print("url=%s minutes=%s" % (url, minutes))

    if dryrun:
        driver.quit()
        return

    try:
        driver.get(url)
        if locator:
            print("Checking Page loaded")
            WebDriverWait(driver, waitlocator).until(
                EC.presence_of_element_located((By.ID, "logo-icon-container")))

        for x in range(minutes):
            time.sleep(60)
            print("Played %s mintues" % x)
    finally:
        driver.quit()

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--linkfile', help='File include link and minutes in one line')
    parser.add_argument('-p', '--proxyfile', help='File include proxy and port each line')

    return parser.parse_args()

args = parseArguments()
#print(args.linkfile)
#print(args.proxyfile)

lstUrl = []
with open(args.linkfile) as fd:
    for one in fd:
        one = one.strip()
        if not one: continue
        url, time = re.split(r'\s+', one)
        lstUrl.append((url, int(time)))

lstProxy = []
with open(args.proxyfile) as fd:
    for one in fd:
        one = one.strip()
        if not one: continue
        lstProxy.append(one)

lstArgs = ['--ignore-certificate-errors']
random.shuffle(lstProxy)
for proxy in lstProxy:
    for one in lstUrl:
        driver = getChromeDriver(lstArgs, proxy)
        waitPlay(driver, one[0], one[1], "logo-icon-container")
