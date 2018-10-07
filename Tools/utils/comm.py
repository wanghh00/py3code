#!/usr/bin/env python
# -*- coding: utf-8  -*-

import os

import logging; LOG = logging.getLogger(__name__)

LOGFMT = '[%(asctime)s %(filename)s:%(lineno)d] %(message)s'
LOGDATEFMT = '%Y%m%d-%H:%M:%S'

def initLOG():
    logging.basicConfig(format=LOGFMT,datefmt=LOGDATEFMT)
    logging.getLogger().setLevel(logging.INFO)

DctFileDesc = {}
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
