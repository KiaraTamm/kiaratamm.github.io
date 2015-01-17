#!/usr/bin/env python

# Raportisto reporting Tool Logging Script
__author__ = 'cryptoassure'

import os
import time

import logging

# Directory where the files need to end up
logDir = os.path.abspath(os.path.join(os.getcwd()))
logFile = os.path.join(logDir,'status.log')

logging.basicConfig(filename=logFile,level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s.%(msecs)dGMT %(module)s - %(funcName)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logging.Formatter.converter = time.gmtime