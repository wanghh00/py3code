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

url = 'https://www.youtube.com/'
driver = webdriverbuilder.ChromeDriverBuilder().getDriver()
driver.get(url)

time.sleep(3)
searchBar = driver.find_element(By.ID, "search")
searchBar.send_keys("理财")

time.sleep(3)
searchButton = driver.find_element(By.ID, "search-icon-legacy")
searchButton.click()

def chkChannel(driver, channelId):
    LOG.info("Checking channel...")
    elem = None
    for one in driver.find_elements(By.CSS_SELECTOR, "#contents a.ytd-channel-renderer"):
        LOG.info(one)
        href = one.get_attribute('href')
        LOG.info(href)
        if href.find(channelId) != -1:
            elem = one
            break
    return elem

def playChannel(driver):
    play = driver.find_element(By.CSS_SELECTOR, "#play-button")
    button = play.find_element(By.CSS_SELECTOR, "a")
    button and button.click()
    #button and button.click()
    time.sleep(60)
    return
    
    elems = driver.find_elements(By.CSS_SELECTOR, "#contents #items ytd-grid-video-renderer")
    LOG.info("hehe... %s" % len(elems))
    for one in driver.find_elements(By.CSS_SELECTOR, "#items ytd-grid-video-renderer"):
        link = one.find_element(By.CSS_SELECTOR, '#thumbnail')
        href = link.get_attribute('href')
        LOG.info(href)
    #random.choice(elemes).click()
    time.sleep(60)

for x in range(10):
    elem = chkChannel(driver, 'UChw72cSGdllVEf3HQRQCjvw')
    if elem:
        elem.click()
        break
    time.sleep(5)
    comm.scrollToBottom(driver)

playChannel(driver)

time.sleep(60)
