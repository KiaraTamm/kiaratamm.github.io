#!/usr/bin/env python

# Raportisto reporting script
__author__ = 'cryptoassure'

# Scope: Iterate through bot directories and extract out relevant
# information from the log files. Use that information to construct
# a new summary.json file that the report web server can simply interact
# with instead of having to use javascript to iterate through lots of
# different exchange_marketpair.json files in a number of directories.

# CUSTODIAN REPORTING STEPS
# =========================

import os
import sys
# access module scripts needed to run this script
sys.path.insert(0, 'scripts')
import log

# start reporting pass
log.logging.critical('STARTING REPORTING RUN')

# STEP 1 : CREATE EXCHANGE PAIR DATA DIRECTORIES 
# ==============================================
# Create new directories for the bot data to be stored in if they don't already exist and put them into the _harp/data directory
import initialize

# STEP 2 : ITERATE THROUGH OPTION FILES AND REMOVE CONFIDENTIAL PARAMETERS
# ========================================================================
# Iterate through each options.json file in the and remove confidential parameters (API keys, location of nu daemon, etc.)
initialize.bot_directories


# STEP 3 : REQUEST TRADE DATA FROM EXCHANGE API
# ========================================================================
# Request current trade data from the active markets via each exchanges' API. Place each of the trade records (for the different time frames) in their respective _harp/data/exchange_marketpair directories.
import trades
trades.fetchTradeData()


# end reporting pass
log.logging.critical('REPORTING RUN COMPLETED')
