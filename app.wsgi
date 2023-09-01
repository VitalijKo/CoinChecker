#!/usr/bin/python3
import sys

sys.path.insert(0, '/var/www/SberbankCoinsMonitorBot/')

from main import app as application

application.secret_key = 'SCMB'
