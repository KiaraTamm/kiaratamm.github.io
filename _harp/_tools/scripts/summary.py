#!/usr/bin/env python

# Raportisto reporting script - summary.py
__author__ = 'cryptoassure'

# scope: generate a summary.json file with high-level operations metadata
#  * Custodian information
#  * Grant information
#  * Dividend information
#  * Funds held 'off-exchange'
#  * Nested array for operating markets

import os
import shutil
import time
import json
import log
import re
import subprocess

import sys
# access configuration files needed to run this script
sys.path.insert(0, 'configuration')
import reportconfig

# initialize where raportisto can find all data and files it will need
root_dir = reportconfig.NUBOTDIRS
# publicly visible directory where we'll copy over files
report_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/"))
# get the base URL for the repository where the report will be publicly visible
report_base_url = reportconfig.REPORTBASEURL


# set up the common timestamp that will be used for future calculations
publication_time = lambda: int(round(time.time() * 1000))
# use 'publication_time()' to inject when needed when needed

# create the main 'summary.json' file (or update, if it aleready exists)
output_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, 'data/summary.json'))

with open(output_file, 'w+') as output:
  # insert grant details and skeleton for future nested data structures
  details_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, '_tools/templates/_grant-details.json'))
  grant_details = []
  grant_details = open(details_file).read()
  data = json.loads(grant_details)

  # update the publication timestamp
  data['reportGenerated'] = publication_time()

  # insert the link to the report's public URL
  data['reportRepository'] = report_base_url

  # load the custodian's grant(s) details
  custodian_grants = os.path.abspath(os.path.join(os.getcwd(), os.pardir, '_tools/configuration/grants.json'))
  custodian_grants_details = []
  custodian_grants_details = open(custodian_grants).read()
  cgdData = json.loads(custodian_grants_details)
  
  # append the custodian's grant information
  data['reportDetails'].append(cgdData)

  # write the details data to the new/updated data.json file
  output_data = json.dumps(data, indent=4, sort_keys=True)
  output.write(output_data)

output.close()

# STEP: append details about each operating market's supported pair(s)
#  * Exchange
#  ** Pair
#  *** Bot Behavior
#  *** NuBot pair configuration file path
#  *** Open orders
#  *** Path to order data file
#  *** Path to wall shift data file
#  *** Trades
#  **** in the last 24 hours
#  **** in the last week
#  **** in the last 30 days
#  **** for all time

def getPrecision(exchangeCurrency):
  # get the level of percision for decimal places depending on the currency
  # being evaluated
  global unitPrecision
  if exchangeCurrency == "btc":
    unitPrecision = 8
  elif exchangeCurrency == "ppc":
    unitPrecision = 6
  elif exchangeCurrency == "eur":
    unitPrecision = 4
  elif exchangeCurrency == "usd":
    unitPrecision = 4
  else:
    unitPrecision = 4

def resetWallShiftFill():
  # call this when a market's wall shift data doesn't exist and the default
  # variable values need to be passed to it
  global wsBuyPrice
  global wsCrypto
  global wsCurrency
  global wsOtherFeeds
  global wsPrice
  global wsSellPrice
  global wsSource

  wsBuyPrice = 0
  wsCrypto = ""
  wsCurrency = ""
  wsOtherFeeds = ""
  wsPrice = 0
  wsSellPrice = 0
  wsSource = ""


def wallShiftFill(market_pair):
  # get the wall shift data from wall_shifts.json for each market pair and
  # insert into summary.json
  global wsBuyPrice
  global wsCrypto
  global wsCurrency
  global wsOtherFeeds
  global wsPrice
  global wsSellPrice
  global wsSource

  wall_shift_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/", market_pair, "wall_shifts.json"))

  if os.path.isfile(wall_shift_file):

    wall_data = []
    wall_data = open(wall_shift_file).read()
    wdata = json.loads(wall_data)

    # check to see if the wall_shifts.json file has actual movement, otherwise, skip the file
    if len(wdata) >= 1:
      wdata = wdata[0]

      # also skip the file if it only contains a repeat of the key for the value
      if not wdata['buyprice'] == "buyprice":

        # if it has actual value, go ahead and assign variables
        wsBuyPrice = float(wdata['buyprice'])
        wsCrypto = wdata['crypto']
        wsCurrency = wdata['currency']
        wsOtherFeeds = wdata['otherfeeds']
        wsPrice = float(wdata['price'])
        wsSellPrice = float(wdata['sellprice'])
        wsSource = wdata['source']
      
    else:
      resetWallShiftFill()

  else:
    resetWallShiftFill()


def resetOrderHistoryFill():
  # call this when a market's orders_history data doesn't exist and the default
  # variable values need to be passed to it
  global ohActiveOrders
  global ohSellTotal
  global ohBuyTotal
  global ohSellOrderCurrency
  global ohBuyOrderCurrency
  global ohSellPaymentCurrency
  global ohBuyPaymentCurrency
  global ohOrderType
  global ohAvgSellPrice
  global ohAvgBuyPrice

  ohActiveOrders = 0
  ohSellTotal = 0
  ohBuyTotal = 0
  ohSellOrderCurrency = ""
  ohBuyOrderCurrency = ""
  ohAvgSellPrice = 0
  ohAvgBuyPrice = 0
  ohSellPaymentCurrency = ""
  ohBuyPaymentCurrency = ""
  ohOrderType = "" 

def calcOrderTotals(market_pair, set_data, data):
  # call this when you need to calculate the totals and assign values for 
  # each of the market's active orders
  each_order = set_data['digest']
  # calculate totals and assign values
  ohSellTotal = []
  ohBuyTotal = []
  ohSellPrice = [0]
  ohBuyPrice = [0]
  ohSellOrderCurrency = ""
  ohBuyOrderCurrency = ""
  ohSellPaymentCurrency = ""
  ohBuyPaymentCurrency = ""
  for order in each_order:
    ohOrderType = order['order_type']
    ohAmount = order['amount']
    ohPrice = order['price']

    if ohOrderType == "SELL":
      ohSellTotal.append(ohAmount)
      ohSellOrderCurrency = order['order_currency']
      ohSellPaymentCurrency = order['payment_currency']
      ohSellPrice.append(ohPrice)

    if ohOrderType == "BUY":
      ohBuyTotal.append(ohAmount)
      ohBuyOrderCurrency = order['order_currency']
      ohBuyPaymentCurrency = order['payment_currency']
      ohBuyPrice.append(ohPrice)


  ohSellTotal = (sum(ohSellTotal))
  ohBuyTotal = (sum(ohBuyTotal))
  ohAvgBuyPrice = reduce(lambda x, y: x + y, ohBuyPrice) / len(ohBuyPrice)
  ohAvgSellPrice = reduce(lambda x, y: x + y, ohSellPrice) / len(ohSellPrice)

  ohSummaryData = data['%s'%(market_pair)]['currentOrders']

  for ohSummaryDataPart in ohSummaryData:
    if ohSummaryDataPart['orderType'] == "BUY":
      ohSummaryDataPart['amount'] = ohBuyTotal
      ohSummaryDataPart['orderCurrency'] = ohBuyOrderCurrency
      ohSummaryDataPart['paymentCurrency'] = ohBuyPaymentCurrency
      ohSummaryDataPart['price'] = ohAvgBuyPrice

    if ohSummaryDataPart['orderType'] == "SELL":
      ohSummaryDataPart['amount'] = ohSellTotal
      ohSummaryDataPart['orderCurrency'] = ohSellOrderCurrency
      ohSummaryDataPart['paymentCurrency'] = ohSellPaymentCurrency
      ohSummaryDataPart['price'] = ohAvgSellPrice


def orderHistoryFill(market_pair, data):
  # get the order history data from orders_history.json for each market pair
  # and insert into summary.json
  global ohActiveOrders
  global ohSellTotal
  global ohBuyTotal
  global ohSellOrderCurrency
  global ohBuyOrderCurrency
  global ohSellPrice
  global ohBuyPrice
  global ohSellPaymentCurrency
  global ohBuyPaymentCurrency
  global ohOrderType
  global ohAvgSellPrice
  global ohAvgBuyPrice

  orders_history_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/", market_pair, "orders_history.json"))

  # check to make sure the file exists for the market pair, if not, skip it and use the default values
  if os.path.isfile(orders_history_file):
    
    # exists, so find the first newest set of orders using the timestamp
    if os.stat(orders_history_file).st_size == 0:
    
    # in some edge cases, the file exists but it doesn't have data in it
    # in that case, remove the file from the directory to clean things up
    # and then run the resetOrdersHistory() method before moving on
      clean_up = ("rm %s"%(orders_history_file))
      clean = subprocess.Popen(clean_up , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      clean.communicate()
      resetOrderHistoryFill()
    
    # otherwise, data exists and it can be processed to use in the summary.json file  
    else:
      order_data = []
      order_data = open(orders_history_file).read()
      odata = json.loads(order_data)
      
      order_sets = []
      order_sets = odata['orders']

      ohTimestamp_collection = []

      for set in order_sets:
        set_data = set
        ohTimestamp_collection.append(set_data['time_stamp'])

      # get the most recent set of data, by timestamp
      ohMaxTimestamp = max(ohTimestamp_collection)

      # while here, get the second largest in case its values need to be fallen back upon
      count = 0
      ts1 = ts2 = float('-inf')
      for x in ohTimestamp_collection:
          count += 1
          if x >= ts1:
              ts1, ts2 = x, ts1
          elif x > ts2:
              ts2 = x
      #print(ts2) if count >= 2 else None
      ohMaxTimestampNext = ts2

      # go back to the orders history data and retrieve the right values
      for set in order_sets:
        set_data = set
        ohTimestamp = set_data['time_stamp']
        if ohTimestamp == ohMaxTimestamp:

          # check to make sure that the set_data isn't one for "0" order
          # if it is, step back one in the index and check that
          if set_data['active_orders'] == 0:
            # go back to the next highest timestamp
            for set in order_sets:
              set_data = set
              ohTimestamp = set_data['time_stamp']
              if ohTimestamp == ohMaxTimestampNext:
                calcOrderTotals(market_pair, set_data, data)
          else:
            calcOrderTotals(market_pair, set_data, data)

        
        else:
          continue

  else:
    resetOrderHistoryFill()

# instantiate variables
unitPrecision = 0
sumSellCount = 0
sumSellValue = 0
sellPrice = []
sumSellFee = 0
sellOrderSize = []
avgSellOrderSize = 0
avgSellPrice = 0
sellValueNBT = []
sellValueExCurrency = []
minSellPrice = 0
maxSellPrice = 0
sellTradeTimestamps = []
lastSellTrade = 0
sellCommission = []

wsBuyPrice = 0
wsCrypto = ""
wsCurrency = ""
wsOtherFeeds = ""
wsPrice = 0
wsSellPrice = 0
wsSource = ""

ohActiveOrders = 0
ohSellTotal = 0
ohBuyTotal = 0
ohSellOrderCurrency = ""
ohBuyOrderCurrency = ""
ohAvgSellPrice = 0
ohAvgBuyPrice = 0
ohSellPaymentCurrency = ""
ohBuyPaymentCurrency = ""
ohOrderType = ""

sumBuyCount = 0
sumBuyValue = 0
buyPrice = []
sumBuyFee = 0
buyOrderSize = []
avgBuyOrderSize = 0
avgBuyPrice = 0
buyValueNBT = []
buyValueExCurrency = []
minBuyPrice = 0
maxBuyPrice = 0
buyTradeTimestamps = []
lastBuyTrade = 0
buyCommission = []

pairURL = ""

def getPairURL(market_pair):
  # look into the helper-urls.json file and pull back data
  global pairURL

  helper_file = "configuration/helper-urls.json"
  helper_data = []
  helper_data = open(helper_file).read()
  data = json.loads(helper_data)

  # use the market_pair to return the pairURL value
  pairURL_data = []
  pairURL_data = data['market_pair']

  for key, value in pairURL_data.items():
    if key == market_pair:
      pairURL = value


def tradeFill(bot_dir, t_range):
  # STEP: Calculate market pair state data and insert it into summary.json
  # TODO: HOOK UP trades.py so that it will generate the list of needed files, first
  trades_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/", bot_dir, "trades_%s.json"%(t_range)))

  sum_trades_tmp = os.path.abspath(os.path.join(TMPdirpath, "TMPsumTrades%s.json"%(t_range)))

  # reset values of variables for each iteration to make sure the data is clean
  global sumSellCount
  global sumSellValue
  global sellPrice
  global sumSellFee
  global avgSellOrderSize
  global avgSellPrice
  global sellValueNBT
  global sellValueExCurrency
  global minSellPrice
  global maxSellPrice
  global sellTradeTimestamps
  global lastSellTrade
  global sellCommission
  sumSellCount = 0
  sumSellValue = 0
  sellPrice = []
  sumSellFee = 0
  sellOrderSize = []
  avgSellOrderSize = 0
  avgSellPrice = 0
  sellValueNBT = []
  sellValueExCurrency = []
  minSellPrice = 0
  maxSellPrice = 0
  sellTradeTimestamps = []
  lastSellTrade = 0
  sellCommission = []

  global sumBuyCount
  global sumBuyValue
  global buyPrice
  global sumBuyFee
  global avgBuyOrderSize
  global avgBuyPrice
  global buyValueNBT
  global buyValueExCurrency
  global minBuyPrice
  global maxBuyPrice
  global buyTradeTimestamps
  global lastBuyTrade
  global buyCommission
  sumBuyCount = 0
  sumBuyValue = 0
  buyPrice = []
  sumBuyFee = 0
  buyOrderSize = []
  avgBuyOrderSize = 0
  avgBuyPrice = 0
  buyValueNBT = []
  buyValueExCurrency = []
  minBuyPrice = 0
  maxBuyPrice = 0
  buyTradeTimestamps = []
  lastBuyTrade = 0
  buyCommission = []

  # parse the individual logs and generate a set of values that will be 
  # inserted into summary.json
  with open(sum_trades_tmp, 'w+') as output:

    trade_data = []
    trade_data = open(trades_file).read()
    data = json.loads(trade_data)

    tradelist = data.keys()

    # from the file name, extract the exchange currency
    exchangeCurrency = bot_dir[-3:]
    # set the precision of rounding used later
    getPrecision(exchangeCurrency)

    # next, test the type of the trade and collect data
    for trade in tradelist:

      def tradeTypeAssignment(switch):
        # used to identify which currency is used in the trade data returned from 
        # the exchange's API to appropriately calculate amount, fee, etc.
        global sumSellCount
        global sumSellValue
        global sellPrice
        global sumSellFee
        global avgSellOrderSize
        global avgSellPrice
        global sellValueNBT
        global sellValueExCurrency
        global minSellPrice
        global maxSellPrice
        global sellTradeTimestamps
        global lastSellTrade
        global sellCommission

        global sumBuyCount
        global sumBuyValue
        global buyPrice
        global sumBuyFee
        global avgBuyOrderSize
        global avgBuyPrice
        global buyValueNBT
        global buyValueExCurrency
        global minBuyPrice
        global maxBuyPrice
        global buyTradeTimestamps
        global lastBuyTrade
        global buyCommission

        if switch == 1:
          # for all "swapped" markets where NBT isn't the base currency
          if type == "SELL":

            # sell commission
            if amount > 0:
              buyCommission.append(fee / amount)

            sumSellCount += 1
            sumSellValue += amount
            sellPrice.append(price)
            sumSellFee += fee
            sellOrderSize.append(amount)
            sellValueNBT.append(amount)
            sellValueExCurrency.append(amount * price)
            sellTradeTimestamps.append(timestamp)
          
          elif type == "BUY":

            # fee for sales needs to be converted from base currency to NBT
            feeConversion = (fee / price)

            # buy commission
            if amount > 0:
              buyCommission.append(feeConversion / amount)

            sumBuyCount += 1
            sumBuyValue += amount
            buyPrice.append(price)
            sumBuyFee += feeConversion
            buyOrderSize.append(amount)
            buyValueNBT.append(amount)
            buyValueExCurrency.append(amount * price)
            buyTradeTimestamps.append(timestamp)

          else:
            log.logging.debug("Something went wrong; no trade type for a valid trade.")
        
        else:
          # for all markets where NBT is the base currency
          if type == "SELL":

            # fee for sales needs to be converted from base currency to NBT
            feeConversion = (fee / price)

            # sell commission
            if amount > 0:
              sellCommission.append(feeConversion / amount)

            sumSellCount += 1
            sumSellValue += amount
            sellPrice.append(price)
            sumSellFee += feeConversion
            sellOrderSize.append(amount)
            sellValueNBT.append(amount)
            sellValueExCurrency.append(amount * price)
            sellTradeTimestamps.append(timestamp)
          
          elif type == "BUY":

            # buy commission
            if amount > 0:
              buyCommission.append(fee / amount)

            sumBuyCount += 1
            sumBuyValue += amount
            buyPrice.append(price)
            sumBuyFee += fee
            buyOrderSize.append(amount)
            buyValueNBT.append(amount)
            buyValueExCurrency.append(amount * price)
            buyTradeTimestamps.append(timestamp)

          else:
            log.logging.debug("Something went wrong; no trade type for a valid trade.")

      type = data[trade]['type']
      price = data[trade]['price']
      fee = data[trade]['fee']
      timestamp = data[trade]['timestamp']

      # if the exchange currency is NBT, values need to be swapped to give the
      # correct amounts, fees, etc. using a converted price
      if exchangeCurrency == "nbt":
        # price will be "NBT per X so amount needs to be translated from "X"
        # to "# of NBTs worth of X"
        amount = (price * amount)
        switch = 1
        tradeTypeAssignment(switch)
      else:
        # the amount is already shown in NBT so no translation needed
        amount = data[trade]['amount']
        switch = 0
        tradeTypeAssignment(switch)


    # sort the arrays
    sellPrice.sort()
    buyPrice.sort()
    sellTradeTimestamps.sort()
    buyTradeTimestamps.sort()

    # process the arrays if trades exist for buy/sell
    if sumSellCount > 0:
      # average sell order size during trade range
      if sum(sellOrderSize) > 0:
        avgSellOrderSize = reduce(lambda x, y: x + y, sellOrderSize) / (len(sellOrderSize))
      else:
        avgSellOrderSize = 0
      # average sell price during trade range
      avgSellPrice = reduce(lambda x, y: x + y, sellPrice) / (len(sellPrice))
      # lowest price that NBT were sold for during trade range
      sellPrice = [i for i in sellPrice if i > 0.000001]
      minSellPrice = min(sellPrice)
      # highest price that NBT were sold for during trade range
      maxSellPrice = max(sellPrice)
      # value of currency sold during trade range (valued as NBT)
      sellValueNBT = sum(sellValueNBT)
      # value of currency sold during trade range (valued in exchange currency)
      sellValueExCurrency = sum(sellValueExCurrency)
      # evaluate the array of timestamps to get the most recent value
      lastSellTrade = max(sellTradeTimestamps)
      # calculate the average of the trade commissions
      if len(sellCommission) >= 1:
        sellCommission = reduce(lambda x, y: x + y, sellCommission) / (len(sellCommission))
        sellCommission = float(round(sellCommission, 3))
      else:
        sellCommission = 0

    else:
      log.logging.debug("No sales recorded in time range")

    if sumBuyCount > 0:
      # average buy order size during trade range
      if sum(buyOrderSize) > 0:
        avgBuyOrderSize = reduce(lambda x, y: x + y, buyOrderSize) / (len(buyOrderSize))
      else:
        avgBuyOrderSize = 0
      # average buy price during trade range
      avgBuyPrice = reduce(lambda x, y: x + y, buyPrice) / (len(buyPrice))
      # lowest price that NBT were bought for during trade range
      buyPrice = [i for i in buyPrice if i > 0.000001]
      minBuyPrice = min(buyPrice)
      # highest price that NBT were bought for during trade range
      maxBuyPrice = max(buyPrice)
      # value of currency bought during trade range (valued as NBT)
      buyValueNBT = sum(buyValueNBT)
      # value of currency bought during trade range (valued in exchange currency)
      buyValueExCurrency = sum(buyValueExCurrency)
      # evaluate the array of timestamps to get the most recent value
      lastBuyTrade = max(buyTradeTimestamps)
      # calculate the average of the trade commissions
      if len(buyCommission) >= 1:
        buyCommission = reduce(lambda x, y: x + y, buyCommission) / (len(buyCommission))
        buyCommission = float(round(buyCommission, 3))
      else:
        buyCommission = 0

    else:
      log.logging.debug("No purchases recorded in time range")

import tempfile

TMPdirpath = tempfile.mkdtemp()

consolidated_mp_data = []
final_data = []

# set global pointer for where the summary file is
summary_file = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data/summary.json"))

# list subdirectories of 'data/'
data_directories = [x[0] for x in os.walk(report_dir)]
for data_dir in data_directories:
  if data_dir == "":
    continue

  market = data_dir.replace(report_dir, "").replace("/", "").split("_")[0]
  market_pair = data_dir.replace(report_dir, "").replace("/", "")

  if market_pair == "":
    continue
  # loop through the data_dir objects and use it as a starting point 
  # to insert into a cloned version of the _marketpair.json template.
  mp_summary_file = os.path.abspath(os.path.join(TMPdirpath, "summary-%s.json"%(market_pair)))

  with open(mp_summary_file, 'w+') as output:
    # insert marketpair skeleton for future population
    mp_template = 'templates/_marketpair.json'

    # function to replace the "market_pair" key name with the 
    # actual market_pair
    def rename_marketpair_key(obj):
      for key in obj.keys():
        new_key = key.replace("market_pair", market_pair)
        if new_key != key:
          obj[new_key] = obj[key]
          del obj[key]
      return obj

    pair_details = []
    pair_details = open(mp_template).read()
    data = json.loads(pair_details, object_hook=rename_marketpair_key)

    # fill in general details for the market pair
    options = 'options.json'
    bot_options_path = (os.path.join(report_dir, market_pair, options))
    bot_options_details = []
    bot_options_details = open(bot_options_path).read()
    bo_data = json.loads(bot_options_details)
    
    # data from the sanitized options.json file
    if bo_data['options']['dualside']:
      data['%s'%(market_pair)]['botBehavior'] = "Dual-side Custodian"
    else:
      data['%s'%(market_pair)]['botBehavior'] = "Liquidity Providing Custodian"
    data['%s'%(market_pair)]['liquidityAddress'] = bo_data['options']['nubitaddress']
    # public URL for options.json 
    data['%s'%(market_pair)]['configuration'] = ("%sdata/%s/options.json"%(report_base_url, market_pair))
    # public URL for orders_history.json
    data['%s'%(market_pair)]['orderDataFile'] = ("%sdata/%s/orders_history.json"%(report_base_url, market_pair))
    # public URL for wall_shifts.json
    data['%s'%(market_pair)]['wallDataFile'] = ("%sdata/%s/wall_shifts.json"%(report_base_url, market_pair))

    # inject each market's wall shift data
    wallShiftFill(market_pair)
    data['%s'%(market_pair)]['wallshifts']['buyPrice'] = wsBuyPrice
    data['%s'%(market_pair)]['wallshifts']['crypto'] = wsCrypto
    data['%s'%(market_pair)]['wallshifts']['currency'] = wsCurrency
    data['%s'%(market_pair)]['wallshifts']['otherFeeds'] = wsOtherFeeds
    data['%s'%(market_pair)]['wallshifts']['price'] = wsPrice
    data['%s'%(market_pair)]['wallshifts']['sellPrice'] = wsSellPrice
    data['%s'%(market_pair)]['wallshifts']['source'] = wsSource

    # inject each market's orders history data
    orderHistoryFill(market_pair, data)

    # get the pairURL for the market
    getPairURL(market_pair)
    data['%s'%(market_pair)]['pairURL'] = pairURL

    # run calculations against trade range data file for each market pair
    tradeRanges = ['alltime','last30days','lastweek','lastday']
    for tradeRange in tradeRanges:
      t_range = tradeRange
      tradeFill(market_pair, t_range)

      # populate trade range temporary file with data from tradeFill function
      rangeTrades = []

      def popRangeData(trdata, unitPrecision):
        # set the URL for the report
        trdata['filePath'] = ("%sdata/%s/trades_%s.json"%(report_base_url, market_pair, t_range))
        
        # sell-side values
        trdata['sell']['orders'] = sumSellCount
        trdata['sell']['sumSales'] = round(sumSellValue, unitPrecision)
        trdata['sell']['sumFees'] = round(sumSellFee, unitPrecision)
        trdata['sell']['avgOrderSize'] = round(avgSellOrderSize, unitPrecision)
        trdata['sell']['avgPrice'] = round(avgSellPrice, unitPrecision)
        trdata['sell']['lowPrice'] = round(minSellPrice, unitPrecision)
        trdata['sell']['highPrice'] = round(maxSellPrice, unitPrecision)
        trdata['sell']['lastTradeTime'] = lastSellTrade
        trdata['sell']['commission'] = sellCommission
        if trdata['sell']['commission'] == []:
          trdata['sell']['commission'] = 0
        
        # buy-side values
        trdata['buy']['orders'] = sumBuyCount
        trdata['buy']['sumSales'] = round(sumBuyValue, unitPrecision)
        trdata['buy']['sumFees'] = round(sumBuyFee, unitPrecision)
        trdata['buy']['avgOrderSize'] = round(avgBuyOrderSize, unitPrecision)
        trdata['buy']['avgPrice'] = round(avgBuyPrice, unitPrecision)
        trdata['buy']['lowPrice'] = round(minBuyPrice, unitPrecision)
        trdata['buy']['highPrice'] = round(maxBuyPrice, unitPrecision)
        trdata['buy']['lastTradeTime'] = lastBuyTrade
        trdata['buy']['commission'] = buyCommission
        if trdata['buy']['commission'] == []:
          trdata['buy']['commission'] = 0

      if t_range == "alltime":
        trdata = data['%s'%(market_pair)]['trades']['lifetime']
      elif t_range == "last30days":
        trdata = data['%s'%(market_pair)]['trades']['thirty']        
      elif t_range == "lastweek":
        trdata = data['%s'%(market_pair)]['trades']['week']
      elif t_range == "lastday":
        trdata = data['%s'%(market_pair)]['trades']['day']
      else:
        log.logging.debug("Not all time")

      popRangeData(trdata, unitPrecision)

    # write the details data to the new/updated data.json file
    output_data = json.dumps(data, indent=4, sort_keys=True)
    output.write(output_data)

  output.close()

  # insert content from each summary-{market_pair}.json into summary.json
  # remove summary-{market_pair}.json temporary files after being processed

  TMPsummary = os.path.abspath(os.path.join(TMPdirpath, "TMPsummary.json"))

  with open(TMPsummary, 'w+') as output:
    summary_data = open(mp_summary_file).read()
    sumdata = json.loads(summary_data)
    consolidated_mp_data.append(sumdata)
    output_data = json.dumps(consolidated_mp_data, indent=4, sort_keys=True)
    output.write(output_data)
  output.close()


# finally, insert the TMPsummary.json data into the summary.json file
with open(summary_file, 'r+') as output:
  # place content from summary-{market_pair}.json into the 
  # "fundsActive" array
  summary_mp_data = consolidated_mp_data

  sumdata = open(summary_file).read()
  data = json.loads(sumdata)

  # build a collection of active grants from TMPsummary.json

  # IMPORTANT!! TEMPORARY
  # TODO: figure out a way to separate bot activity when split between
  # different grants -- for now, assume that there will only be one 'active'
  # grant listed in configuration/grants.json

  data['reportDetails'][0]['grants'][0]['fundsActive'].append(summary_mp_data)

  output_data = json.dumps(data, indent=4, sort_keys=True, separators=(',', ':'))
  output.write(output_data)

output.close()


# STEP: other reporting steps

# STEP: Clean up temporary files
shutil.rmtree(TMPdirpath)