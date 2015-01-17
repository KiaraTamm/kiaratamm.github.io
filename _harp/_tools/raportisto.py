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
# ============================================================================
# Create new directories for the bot data to be stored in if they don't already exist and put them into the _harp/data directory
import initialize


# STEP 2 : ITERATE THROUGH OPTION FILES AND REMOVE CONFIDENTIAL PARAMETERS
# ============================================================================
# Iterate through each options.json file in the and remove confidential parameters (API keys, location of nu daemon, etc.)
# (included in initialize.py)


# STEP 3 : ITERATE THROUGH LATEST BOT LOG FILES AND CREATE WALL_SHIFTS.JSON
# ============================================================================
# Iterate through each bot's 'logs' directory and copy the wall_shifts.json file from the most recent one to the matching exchange pair data directory.
# (included in initialize.py)


# STEP 4 : ITERATE THROUGH LATEST BOT LOG FILES AND CREATE ORDERS_HISTORY.JSON
# ============================================================================
# Iterate through each bot's 'logs' directory and copy the orders_history.json file from the most recent one to the matching exchange pair data directory.
# (included in initialize.py)


# STEP 5 : REQUEST TRADE DATA FROM EXCHANGE API
# ============================================================================
# Request current trade data from the active markets via each exchanges' API. Place each of the trade records (for the different time frames) in their respective _harp/data/exchange_marketpair directories.
import trades
trades.fetchTradeData()

# STEP 6 : CREATE INITIAL SUMMARY.JSON
# ============================================================================
# Generate a summary.json file with high-level operations metadata
#  * Custodian information
#  * Grant information
#  * Dividend information
#  * Funds held 'off-exchange'
#  * Nested array for operating markets' data
import summary

# end reporting pass
log.logging.critical('REPORTING RUN COMPLETED')
