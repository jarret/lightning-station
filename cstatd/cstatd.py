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
from sys_stats import SysStats


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE = os.path.join(CONFIG_DIR, "cstatd.log")
setup_logging(LOG_FILE, "cstatd", console_silent=True,
              min_level=logging.DEBUG)

PUBLISH_ENDPOINT = config['Cstatd']['ZmqPubEndpoint']

FETCH_DELAY = 0.01

class Cstatd(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)

    def publish(self, tag, message):
        #logging.info("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)

    ###########################################################################

    def fetch_cpu_stats_callback(self, stats):
        if stats:
            for tag, value in stats:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(2.0, self.start_cpu_stat_fetch)

    def start_cpu_stat_fetch(self):
        d = threads.deferToThread(SysStats.get_cpu_stats)
        d.addCallback(self.fetch_cpu_stats_callback)

    def fetch_mem_stats_callback(self, stats):
        if stats:
            for tag, value in stats:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(1.0, self.start_mem_stat_fetch)

    def start_mem_stat_fetch(self):
        d = threads.deferToThread(SysStats.get_mem_stats)
        d.addCallback(self.fetch_mem_stats_callback)

    def fetch_net_stats_callback(self, stats):
        if stats:
            for tag, value in stats:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(1.0, self.start_net_stat_fetch)

    def start_net_stat_fetch(self):
        d = threads.deferToThread(SysStats.get_net_stats)
        d.addCallback(self.fetch_net_stats_callback)

    ###########################################################################

    def start(self):
        reactor.callLater(0.1, self.start_net_stat_fetch)
        reactor.callLater(0.1, self.start_cpu_stat_fetch)
        reactor.callLater(0.1, self.start_mem_stat_fetch)

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
    p = Cstatd()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
