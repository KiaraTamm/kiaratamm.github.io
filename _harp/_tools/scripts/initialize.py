#!/usr/bin/env python

# Raportisto Reporting Tool - initialize.py
__author__ = 'cryptoassure'

# scope: initialize exchange data directories if they don't already exist

import os
import shutil
import sys
# access configuration files needed to run this script
sys.path.insert(0, 'configuration')
import reportconfig
# access module scripts needed to run this script
sys.path.insert(0, 'scripts')
import log

# initialize where raportisto can find all data and files it will need
root_dir = reportconfig.NUBOTDIRS
log.logging.critical('Bot directory root path: %s'%(root_dir))
# publicly visible directory where we'll copy over files
report_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/"))
log.logging.critical("Path to report data: %s"%(report_dir))
# get the base URL for the repository where the report will be publicly visible
report_base_url = reportconfig.REPORTBASEURL
log.logging.critical("Public URL (base) for report: %s"%(report_base_url))


# clean the _harp/data directory state by deleting any pre-existing
# directories and files
report_directories = []
for dirs in os.listdir(report_dir):
  rd = os.path.join(report_dir, dirs)
  if os.path.isdir(rd):
    report_directories.append(rd)

for report in report_directories:
  if report == "":
    continue
  clean_dir = (os.path.join(report_dir, report))
  log.logging.debug("Cleaning directory: %s"%(clean_dir))
  shutil.rmtree(clean_dir, ignore_errors=True)


# get subdirectories, one for each bot
bot_directories = []
bot_log_directories = []
for d in os.listdir(root_dir):
  bd = os.path.join(root_dir, d)
  if os.path.isdir(bd):
    bot_directories.append(bd)
    logs = os.path.join(bd, 'logs/')
    bot_log_directories.append(logs)

for bot_dir in bot_directories:
  if bot_dir == "":
    continue
  # create directories to hold reporting logs
  bot_root_dir = bot_dir.replace(root_dir, "").replace(os.sep, "")
  new_dir = (os.path.join(report_dir, bot_root_dir))
  log.logging.debug("Creating directory: %s"%(new_dir))
  os.makedirs(new_dir)

# check to see if summary.json exists already and if so, delete it
# it will be recreated later
summary_path = os.path.join(report_dir, 'summary.json')
try:
  if os.path.isfile(summary_path):
    log.logging.debug("Removing existing summary.json")
    os.unlink(summary_path)
except Exception, e:
  print e

log.logging.debug("Initialization Complete.")
