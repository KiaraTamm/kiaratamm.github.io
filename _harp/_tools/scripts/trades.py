#!/usr/bin/env python

# Raportisto reporting script - trades.py
__author__ = 'cryptoassure'

# scope: poll each of the exchanges' APIs to pull back trade data 
# (by time range) from each of the accounts on the exchange and place
# a copy of it in the corresponding _harp/data/exchange_pair directory

import os
import json
import time
import datetime
import subprocess

import log

# variables
exchange = ""
apitoken = ""
secret = ""
pair = ""
reportRange = ""
timefr = ""
dirPair = ""

class fetchTradeData():

  global exchange
  global apitoken
  global secret
  global pair
  global reportRange
  global timefr
  global dirPair
  global data_dir
  global tools_dir
  tools_dir = ""
  data_dir = ""

  # time variables 
  now = int(datetime.datetime.now().strftime("%s"))
  daysec = (24 * 60 * 60)
  weeksec = (7 * daysec)
  thirtydaysec = (30 * daysec)
  launch = (1411480800)
  yesterday = (now - daysec)
  lastweek = (now - weeksec)
  lastmonth = (now - thirtydaysec)

  log.logging.info('Collecting trade data from exchanges')

  tools_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "_tools/"))
  data_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/"))

  # clear tools directory in case any extra trade files were left from a
  # previous run of the reporting tool
  clear_file = ("rm %s/last_trades_*.json" % (tools_dir))
  cf = subprocess.Popen(clear_file , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  cf.communicate()


  # configurations for each bot
  jason_data=[]
  json_data=open(os.path.join(tools_dir, "configuration/exchange-tokens.json")).read()
  data = json.loads(json_data)

  def populateTrades():
    i = 0
    while i == 0:
      # request the trade results from the exchange's API
      request_results = "java -jar NuGetLastTrades.jar %s \"%s\" \"%s\" %s %d > /dev/null 2>&1" % (exchange, apitoken, secret, pair, reportRange)
      rr = subprocess.Popen(request_results , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      log.logging.debug("Processing (%s, %s, %s)" %(exchange, pair, timefr))
      rr.communicate()

      # move results to exchange/pair directory
      move_results_path = os.path.join(data_dir, "%s_%s/trades_%s.json" % (exchange, dirPair, timefr))
      move_results = ("mv last_trades_*.json %s" % (move_results_path))
      mv = subprocess.Popen(move_results , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      log.logging.debug("Moving results to %s" % (move_results_path))
      mv.communicate()

      # confirm that the results were actually retrieved, if not, retry
      trade_results = os.path.join(data_dir, "%s_%s/trades_%s.json" % (exchange, dirPair, timefr))
      ftest = os.path.isfile(trade_results)
      if not os.path.isfile(trade_results):
        # something went wrong, retry
        log.logging.critical("File was not created for %s, retrying..." % (trade_results))
        i = 0
      
      else:
        i = 1

  # iterate through the different bots
  for d in data["bots"]:

    if d["status"] == "active":
      # run the NuGetLastTrades.jar micro-app only if the bot is listed as 'active'
      exchange = d['market']
      apitoken = d['token']
      secret = d['secret']
      pair = d['pair']

      reportRange = ["yesterday","lastweek","lastmonth","all"]

      # translate 'pair' into format used for directory
      dirPair = d["pair"].replace("_", "")

      for report in reportRange:
        if report == "yesterday":
          reportRange = yesterday
          timefr = "lastday"
          populateTrades()
        elif report == "lastweek":
          reportRange = lastweek
          timefr = "lastweek"
          populateTrades()
        elif report == "lastmonth":
          reportRange = lastmonth
          timefr = "last30days"
          populateTrades()
        elif report == "all":
          reportRange = launch
          timefr = "alltime"
          populateTrades()
        else:
          reportRange = d["range"]
          timefr = "custom"
          populateTrades()

    else:
      exchange = d['market']
      pair = d["pair"]
      log.logging.warning("Skipping inactive bot (%s, %s)..." % (exchange, pair))
   

  # clean out temporary tools/logs/ directory
  tmpLogDir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, '_tools/logs/'))
  clean_temp_logs = ("rm -r %s" % (tmpLogDir))
  ctl = subprocess.Popen(clean_temp_logs , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ctl.communicate()
  log.logging.info("Cleaned up temporary log directory.")

  log.logging.info('Completed trades.py')
