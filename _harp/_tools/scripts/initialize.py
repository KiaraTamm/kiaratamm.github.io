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
import json, csv
import subprocess

ws_file = ""
new_file = ""

def sanitizeOptions(bot_dir, new_dir):
  # iterate through the options.json file and remove confidential information
  options = 'options.json'
  bot_options_path = (os.path.join(bot_dir, options))
  #log.logging.debug("Cloning and sanitizing options.json file for %s"%(bot_options_path))

  # create a new file (or overwrite an existing) used for reporting
  new_options_file = os.path.join(new_dir, 'options.json')
  with open(new_options_file, 'w+') as output:
    options_data = []
    options_data = open(bot_options_path).read()
    data = json.loads(options_data)

    # sanitize the options.json file
    obscure = "private"
    data['options']['apikey'] = obscure
    data['options']['apisecret'] = obscure
    data['options']['nudip'] = obscure
    data['options']['nudport'] = obscure
    data['options']['rpcpass'] = obscure
    data['options']['rpcuser'] = obscure
    data['options']['mail-recipient'] = obscure

    output_data = json.dumps(data, indent=4, sort_keys=True)
    output.write(output_data)

  output.close()


def cleanup():
  #clean up the temporary 'orders_history.csv' file
  if os.path.isfile(new_file):
    rmpf = "rm %s" % (new_file)
    rm = subprocess.Popen(rmpf , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rm.communicate()

def getWallShifts(log_dir, new_dir):
  global ws_file
  global new_file

  ws_csv = 'wall_shifts.csv'
  ws_file = os.path.join(log_dir, ws_csv)
  new_file = os.path.join(new_dir, ws_csv)
  new_shifts = new_file
  reduced_json = 'wall_shifts.json'
  json_path = os.path.join(new_dir, reduced_json)

  # strip the wall_shifts.csv file down to the last entry using `tail`
  # before processing in a temporary file, 'orders_history.csv'
  reduce_orders = ("tail -n 2 %s > %s" % (ws_file, new_shifts))
  ro = subprocess.Popen(reduce_orders , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ro.communicate()

  # check to make sure that a file was created, if not, create a placeholder

  if os.path.isfile(new_shifts):

    # open .csv
    f = open(new_shifts, 'r+')
    reader = csv.DictReader( f, fieldnames = ( "timestamp", "source", "crypto", "price", "currency", "sellprice", "buyprice", "otherfeeds" ))

    # parse the .csv into .json
    pre_out = [ row for row in reader ]
    pre_out_test = ""
    try:
      # confirm that the file even has content in it (markets with no wall shifts, for instance)
      pre_out_test = pre_out[0]['timestamp']
    except IndexError:
      log.logging.critical("There is a problem")
    
    if pre_out_test == "timestamp":
      # this doesn't contain data, so disregard it and move on...
      cleanup()
      log.logging.critical("There is a problem")
    elif pre_out_test == "":
      # this also doesn't contain data, so disregard it and move on...
      cleanup()
      log.logging.critical("There is a problem")      

    else:
      out = json.dumps(pre_out, indent=4, sort_keys=True)

      # save the .json
      f = open(json_path, 'w+' )
      f.write(out)

      cleanup()

  else:
    # exception case
    log.logging.debug("DEBUG > Something went wrong.")


def getOrdersHistory(log_dir, new_dir):
  global oh_file
  global new_file

  oh_json = 'orders_history.json'
  oh_file = os.path.join(log_dir, oh_json)
  new_file = os.path.join(new_dir, oh_json)
  new_history = new_file

  move_orders = ("cp %s %s" % (oh_file, new_history))
  mo = subprocess.Popen(move_orders , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  mo.communicate()

global root_dir
global report_dir
global report_base_url
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

# identify the most recent log sub-directories from each of the active bots
latest_logs_directories = []
for bot_log in bot_log_directories:
  if bot_log == "":
    continue

  all_log_directories = []
  for d in os.listdir(bot_log):
    bd = os.path.join(bot_log, d)
    if os.path.isdir(bd):
      all_log_directories.append(bd)
  latest_logs_directories.append(max(all_log_directories, key=os.path.getmtime))

# iterate through each of the bot directories and grab the appropriate files
for bot_dir in bot_directories:
  if bot_dir == "":
    continue
  # create directories to hold reporting logs
  bot_root_dir = bot_dir.replace(root_dir, "").replace(os.sep, "")
  new_dir = (os.path.join(report_dir, bot_root_dir))
  log.logging.debug("Creating directory: %s"%(new_dir))
  os.makedirs(new_dir)

  # get the options.json file and sanitize it
  sanitizeOptions(bot_dir, new_dir)


# iterate through the latest log directories and set the variables needed
for log_dir in latest_logs_directories:
  if log_dir == "":
    continue

  # place it in the right bot reporting directory
  # see if the director(y)(ies) already exist, if not, create them
  market = log_dir.split("_")[3]
  pair = log_dir.split("_")[4].lower()
  market_pair = ("%s_%s" %(market, pair))
  new_dir = (os.path.join(report_dir, market_pair))

  # create the wall_shifts.json file from the bot's latest log directory
  # wall_shifts.csv file
  getWallShifts(log_dir, new_dir)
  # create the orders_history.json file from the bot's latest log directory
  # orders_history.json
  getOrdersHistory(log_dir, new_dir)


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
