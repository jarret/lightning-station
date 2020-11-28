#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
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

from block_listener import BlockListener
from logger import setup_logging
from bitcoind import Bitcoind
from exec_grind import ExecGrind


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE = os.path.join(CONFIG_DIR, "grindd.log")
setup_logging(LOG_FILE, "grindd", console_silent=True,
              min_level=logging.DEBUG)

PUBLISH_ENDPOINT = config['Grindd']['ZmqPubEndpoint']

Bitcoind.URL = Bitcoind.gen_url(host=config['Grindd']['BitcoindHost'],
                                port=config['Grindd']['BitcoindPort'],
                                user=config['Grindd']['BitcoindUser'],
                                password=config['Grindd']['BitcoindPassword'])

BLOCKS_HISTORY = 10

class Grindd(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)
        self.block_listener = BlockListener(config, self.new_block_cb)

        self.exec_grind =  ExecGrind()
        self.window_data = {}
        self.grind_running = False
        self.grind_blocks = None

    def publish(self, tag, message):
        #logging.info("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)

    ###########################################################################

    def grind_result_cb(self, height, result):
        self.grind_running = False
        self.window_data[height] = result
        self.start_blockchaininfo()

    def set_window(self, height):
        blocks = set(range(height + 1 - BLOCKS_HISTORY, height + 1))
        self.window_data = {h: d for h, d in self.window_data.items() if
                            h in blocks}

    def kickoff_grind(self, height):
        #print("dict: %s" % self.window_data)
        blocks = list(reversed(range(height + 1 - BLOCKS_HISTORY, height + 1)))
        for block in blocks:
            print("trying: %d" % block)
            #print("keys: %s" % self.window_data.keys())
            if block in self.window_data.keys():
                continue
            print("executing: %d" % block)
            self.grind_running = True
            self.exec_grind.run(block, self.grind_result_cb)
            return

    def handle_blockchaininfo(self, info):
        height = info['blocks']
        print("block: %d headers %d" % (info['blocks'], info['headers']))
        if info['headers'] > height:
            # not synced, wait
            return
        self.set_window(height)
        if not self.grind_running:
            self.kickoff_grind(height)

    def getblockchaininfo_callback(self, blockchaininfo):
        if blockchaininfo:
            self.handle_blockchaininfo(blockchaininfo)
        #reactor.callLater(1.0, self.start_blockchaininfo)

    def start_blockchaininfo(self):
        d = threads.deferToThread(Bitcoind.getblockchaininfo)
        d.addCallback(self.getblockchaininfo_callback)

    ###########################################################################

    def new_block_cb(self, block_hash):
        logging.info("block hash: %s" % block_hash)
        self.start_blockchaininfo()

    def start(self):
        reactor.callLater(1.0, self.start_blockchaininfo)

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
    p = Grindd()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
