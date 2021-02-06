#!/usr/bin/env python3
# Copyright (c) 2021 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
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

from pyln.client import LightningRpc


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE = os.path.join(CONFIG_DIR, "lstatd.log")
setup_logging(LOG_FILE, "lstatd", console_silent=True,
              min_level=logging.INFO)

LIGHTNING_RPC = LightningRpc(config['Lstatd']['LightningRpc'])
PUBLISH_ENDPOINT = config['Lstatd']['ZmqPubEndpoint']


class Lstatd(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)

    def publish(self, tag, message):
        #logging.info("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)

    def publish_info(self, info):
        for tag, message in info.items():
            message = json.dumps(message).encode("utf8")
            tag = tag.encode("utf8")
            self.publish(tag, message)


    ###########################################################################

    @staticmethod
    def get_info():
        info = LIGHTNING_RPC.getinfo()
        if not info:
            return None
        return {'ln_version':           info['version'],
                'ln_alias':             info['alias'],
                'ln_inet_peers':        info['num_peers'],
                'ln_channels_pending':  info['num_pending_channels'],
                'ln_channels_active':   info['num_active_channels'],
                'ln_channels_inactive': info['num_inactive_channels']}

    def get_info_callback(self, info):
        print("cb: %s" % info)
        if info:
            self.publish_info(info)
        reactor.callLater(5.0, self.start_get_info)

    def start_get_info(self):
        d = threads.deferToThread(Lstatd.get_info)
        d.addCallback(self.get_info_callback)

    ###########################################################################

    def start(self):
        reactor.callLater(0.1, self.start_get_info)

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
    l = Lstatd()
    l.start()
    reactor.addSystemEventTrigger("before", "shutdown", l.stop)
    reactor.run()
