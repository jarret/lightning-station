#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import urwid
import logging

from configparser import ConfigParser

from info import Info
from screen import Screen
from logger import setup_logging

from twisted.internet import reactor

from subscribe import Subscribe

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

PRICE_SUB_ENDPOINT = config['Panel']['ZmqSubPriceEndpoint']

LOG_FILE = os.path.join(CONFIG_DIR, "panel.log")

if __name__ == "__main__":
    setup_logging(LOG_FILE, "panel", console_silent=True,
                  min_level=logging.DEBUG)
    info = Info(config)
    subscribe = Subscribe(config, info)
    screen = Screen(info, reactor)
    screen.run()
