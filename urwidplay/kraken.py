#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
import logging
import krakenex
import time

from info import Info
from screen import Screen
from logger import setup_logging

from twisted.internet import reactor

LOG_FILE = "/tmp/urwidplay-kraken.log"

if __name__ == "__main__":
    setup_logging(LOG_FILE, "urwidplay", console_silent=True,
                  min_level=logging.DEBUG)



    k = krakenex.API()

    while True:
        print("abc")

        ticker = k.query_public('Ticker', {'pair': 'XXBTZCAD'})

        last_close_raw = ticker["result"]["XXBTZCAD"]["c"]
        last_close = last_close_raw[0]

        timenow = time.strftime("%H:%M:%S")

        print("%s ----> %s\n----------" % (timenow, last_close))
        time.sleep(2.0)
