#!/usr/bin/env python
# -*- coding: utf-8  -*-

from selenium import webdriver

import platform
import logging; LOG = logging.getLogger(__name__)

from . import comm

comm.initLOG()

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
