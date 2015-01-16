#!/usr/bin/env python
__author__ = 'cryptoassure'

# IMPORTANT! Before running the reporting tool, save the updated file 
# as 'reportconfig.py'.

# scope: configurable data used by Raportisto to generate the custodian's
# public NuBot operations report.

# path to NuBot instance directories are found (typically, '~/bots')
NUBOTDIRS = ''

# public base URL for where the report will be published (e.g. 'https://githubaccount.github.io/')
REPORTBASEURL = ''

# path to local git directory that is tied to the remote repository where
# updates will be published to automatically (usually the base directory that)
# this tool lives in, renamed from "raportisto" to "githubaccount.github.io/" 
# to match the repository it is going to be served from.
GITDIR = ''

# TODO: add additional variables for:
# FREQUENCY (how often does the reporting tool automatically run?)
# DATABASE (future versions of Raportisto will have a historical data database)