#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import argparse
import requests

import os
import time, sys, re, random
import logging; LOG = logging.getLogger(__name__)

from utils import comm
from utils import webdriverbuilder

fireFoxDriverBuilder = webdriverbuilder.FireFoxDriverBuilder()
chromeDriverBuilder = webdriverbuilder.ChromeDriverBuilder()

#SPYSURLS = ["http://spys.one/free-proxy-list/US/", "http://spys.one/free-proxy-list/US/1/", 
#    "http://spys.one/free-proxy-list/CA/", "http://spys.one/free-proxy-list/CA/1/", 
#    "http://spys.one/free-proxy-list/AU/", "http://spys.one/free-proxy-list/AU/1/",
#    "http://spys.one/free-proxy-list/UK/", "http://spys.one/free-proxy-list/UK/1/",
#    "http://spys.one/free-proxy-list/NZ/", "http://spys.one/free-proxy-list/NZ/1/"]

SPYSURLS = ["http://spys.one/free-proxy-list/US/", "http://spys.one/free-proxy-list/US/1/",
    "http://spys.one/free-proxy-list/CA/", "http://spys.one/free-proxy-list/CA/1/",
    "http://spys.one/free-proxy-list/UK/", "http://spys.one/free-proxy-list/UK/1/"]
US_PROXY_ORG = ["https://www.us-proxy.org/", "https://free-proxy-list.net/uk-proxy.html"]

comm.initLOG()

#print(requests.get(SPYSURLS[0]).text)
#sys.exit(0)

def parseHtmlFromUSProxyOrg(html):
    ret = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', id='proxylisttable')
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) < 8 or not tds[2].contents[0] in ['US','GB'] or not tds[4].contents[0] == 'elite proxy' \
                    or not tds[6].contents[0] == 'yes':
                continue
            ret.append("%s:%s" % (tds[0].contents[0], tds[1].contents[0]))
    except Exception as ex:
        LOG.exception(ex)
    return ret

def parseSPYS(driver):
    ret = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.spy1x") + driver.find_elements(By.CSS_SELECTOR, "tr.spy1xx")
    for row in rows:
        cols = row.find_elements(By.CSS_SELECTOR, "td")
        LOG.info("%s %s %s" % (cols[0].text, cols[1].text, cols[2].text))
        if cols[1].text != "HTTPS" or cols[2].text != "HIA":
            continue
        ret.append(cols[0].text.split(" ")[1])
    return ret


outFile, driver = None, None
try:
    outFile = open(sys.argv[1], 'w')

    # handle US_PROXY_ORG
    for one in US_PROXY_ORG:
        outFile.write("\n#%s\n" % one)
        for proxy in parseHtmlFromUSProxyOrg(requests.get(one).text):
            outFile.write("%s\n" % proxy)
    
    # handle SPYSURLS
    driver = chromeDriverBuilder.addArgument("--headless").getDriver()
    for one in SPYSURLS:
        outFile.write("\n#%s\n" % one)
        driver.get(one)
        for proxy in parseSPYS(driver):
            outFile.write("%s\n" % proxy)

except Exception as ex:
    LOG.exception(ex)
finally:
    driver and driver.close()
    outFile and outFile.close()