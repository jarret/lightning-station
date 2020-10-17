#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
import logging

from info import Info
from screen import Screen
from logger import setup_logging

from twisted.internet import reactor

LOG_FILE = "/tmp/urwidplay.log"

if __name__ == "__main__":
    setup_logging(LOG_FILE, "urwidplay", console_silent=True,
                  min_level=logging.DEBUG)
    info = Info()
    screen = Screen(info, reactor)
    screen.run()
