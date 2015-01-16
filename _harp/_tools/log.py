#!/usr/bin/env python

# Custodian Reporting Tool Logging Script
__author__ = 'cryptoassure'

import os
import time

import logging

# Directory where the files need to end up
logDir = os.path.abspath(os.path.join(os.getcwd()))
logFile = os.path.join(logDir,'status.log')

logging.basicConfig(filename=logFile, level=logging.DEBUG, format="%(asctime)s GMT; %(levelname)s; %(message)s")
logging.Formatter.converter = time.gmtime