#!/usr/bin/env python

# Raportisto reporting script - publish.py
__author__ = 'cryptoassure'

# scope: take changes and publish them to the custodian's github repository

import os
import shutil
import subprocess
import log

import sys
# access configuration files needed to run this script
sys.path.insert(0, 'configuration')
import reportconfig

# path to the local git repository
git_local_path = reportconfig.GITDIR

from datetime import datetime
git_pub_time = datetime.utcnow()

# compile static content
gen_static = ("cd %s && harp compile _harp ./" % (git_local_path))
gs = subprocess.Popen(gen_static, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
log.logging.info("Compiling static content")
gs.communicate()

if reportconfig.PUBLISH_TO_GIT == True:
  # add to the local git branch, commit changes, publish to the custodian's 
  # remote github repo
  git_build = ('cd %s;git add -A;git commit -avm"Automated report publishing - %s";torify git push origin master' % (git_local_path, git_pub_time))
  gb = subprocess.Popen(git_build, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  log.logging.info("Pushing report to github repository")
  gb.communicate()

else:
  log.logging.info("PUBLISH_TO_GIT == false")
