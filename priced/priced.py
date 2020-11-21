#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import json
import logging

from configparser import ConfigParser

from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from twisted.internet import threads

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection, ZmqPubConnection

from logger import setup_logging
from kraken_price import KrakenPrice


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

FETCH_DELAY = int(config['Priced']['FetchDelay'])
PUBLISH_ENDPOINT = config['Priced']['ZmqPubEndpoint']
LOG_FILE = os.path.join(CONFIG_DIR, "priced.log")
setup_logging(LOG_FILE, "priced", console_silent=True,
              min_level=logging.DEBUG)


class Priced(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)

    def publish_price(self, tag, message):
        print("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)

    ###########################################################################

    def fetch_btccad_callback(self, btccad):
        if btccad:
            print("BTCCAD: %0.2f" % float(btccad))
            message = {'price_btccad': float(btccad)}
            message = json.dumps(message).encode("utf8")
            tag = "price_btccad".encode("utf8")
            self.publish_price(tag, message)
            reactor.callLater(FETCH_DELAY, self.start_btccad)

    def start_btccad(self):
        d = threads.deferToThread(KrakenPrice.fetch_btccad)
        d.addCallback(self.fetch_btccad_callback)

    ###########################################################################

    def start(self):
        reactor.callLater(0.1, self.start_btccad)

    def stop(self):
        pass

    def startService(self):
        super().startService()
        self.start()

    def stopService(self):
        super().stopService()
        self.stop()
        time.sleep(0.5)
        reactor.stop()

if __name__ == "__main__":
    p = Priced()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
