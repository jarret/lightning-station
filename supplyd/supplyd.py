#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import json
import time
import logging

import schedule

from configparser import ConfigParser

from twisted.application.service import Service
from twisted.internet import threads, reactor
from twisted.internet.task import LoopingCall

from twisted.internet import threads

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection, ZmqPubConnection

from logger import setup_logging
from bitcoind import Bitcoind
from block_listener import BlockListener

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

PUBLISH_ENDPOINT = config['Supplyd']['ZmqPubEndpoint']
LOG_FILE = os.path.join(CONFIG_DIR, "supplyd.log")
setup_logging(LOG_FILE, "supplyd", console_silent=True,
              min_level=logging.DEBUG)


Bitcoind.URL = Bitcoind.gen_url(host=config['Bstatd']['BitcoindHost'],
                                port=config['Bstatd']['BitcoindPort'],
                                user=config['Bstatd']['BitcoindUser'],
                                password=config['Bstatd']['BitcoindPassword'])


reward = [50, 25, 12.5, 6.25, 3.125, 1.5625]


class Supplyd(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)
        self.block_listener = BlockListener(config, self.new_block_cb)
        self.running = False
        self.current_block = 0
        self.measured_block = 0
        self.meaasured_supply = 0

    def publish_supply(self, supply):
        message = {'total_supply': supply}
        message = json.dumps(message).encode("utf8")
        tag = "total_supply".encode("utf8")
        logging.info("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)


    ###########################################################################

    @staticmethod
    def perfect_supply(height):
        # assuming
        HALVING_INTERVAL = 210000
        COIN = 100000000
        sup = 0.0
        halvings = height // HALVING_INTERVAL
        for i in range(halvings):
            subsidy = 50 * COIN
            subsidy = subsidy >> i
            sup += subsidy * HALVING_INTERVAL
        remaining = height % HALVING_INTERVAL
        subsidy = 50 * COIN
        subsidy = subsidy >> halvings
        sup += subsidy * remaining
        return sup / 100000000

    @staticmethod
    def perfect_supply_added(start, end):
        return Supplyd.perfect_supply(end) - Supplyd.perfect_supply(start)

    ###########################################################################

    def post_new_utxo_supply(self, block, supply):
        print("post: %s %s" % (block, supply))

    def utxo_scan_task_cb(self, txoutsetinfo):
        self.running = False
        if txoutsetinfo:
            block = result['height']
            supply = result['total_amount']
            self.post_new_utxo_supply(block, supply)

    def kickoff_utxo_scan_task_main(self):
        if self.running:
            print("already running, not doing task")
            return
        print("doing task")
        self.running = True
        d = threads.deferToThread(Bitcoind.gettxoutsetinfo)
        d.addCallback(self.utxo_scan_task_cb)

    def kickoff_utxo_scan_task(self):
        reactor.callFromThread(self.kickoff_utxo_scan_task_main)

    ###########################################################################

    def getblockchaininfo_callback(self, blockchaininfo):
        if blockchaininfo:
            blocks = blockchaininfo['blocks']

    def start_blockchaininfo(self):
        d = threads.deferToThread(Bitcoind.getblockchaininfo)
        d.addCallback(self.getblockchaininfo_callback)

    def new_block_cb(self, block_hash):
        print("block hash: %s" % block_hash)
        self.start_blockchaininfo()

    ###########################################################################

    @staticmethod
    def run_tasks():
        print("run tasks")
        schedule.run_pending()

    def run_tasks_cb(self, result):
        print("callback")
        reactor.callLater(5.0, self.start_thread)

    def start_thread(self):
        d = threads.deferToThread(Supplyd.run_tasks)
        d.addCallback(self.run_tasks_cb)

    def start(self):
        print("start")
        schedule.every(10).seconds.do(self.kickoff_utxo_scan_task)
        #schedule.every().day.at("10:30").do(self.boof)
        self.start_thread()

    def stop(self):
        schedule.clear()
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
    p = Supplyd()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
