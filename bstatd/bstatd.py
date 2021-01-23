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


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE = os.path.join(CONFIG_DIR, "bstatd.log")
setup_logging(LOG_FILE, "bstatd", console_silent=True,
              min_level=logging.INFO)

PUBLISH_ENDPOINT = config['Bstatd']['ZmqPubEndpoint']

Bitcoind.URL = Bitcoind.gen_url(host=config['Bstatd']['BitcoindHost'],
                                port=config['Bstatd']['BitcoindPort'],
                                user=config['Bstatd']['BitcoindUser'],
                                password=config['Bstatd']['BitcoindPassword'])

FEE_RATE_BLOCKS = [1, 5, 25, 50, 100, 250, 500]


class Bstatd(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)
        self.block_listener = BlockListener(config, self.new_block_cb)

    def publish(self, tag, message):
        #logging.info("publishing %s %s" % (tag, message))
        self.pub_connection.publish(message, tag=tag)

    ###########################################################################

    def getmempoolinfo_callback(self, mempoolinfo):
        if mempoolinfo:
            ms = [('mempool_txes', mempoolinfo['size']),
                  ('mempool_bytes', mempoolinfo['bytes']),
                  ('mempool_mem_max', mempoolinfo['maxmempool']),
                  ('mempool_mem_used', mempoolinfo['usage'])]
            for tag, value in ms:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(1.0, self.start_mempoolinfo)

    def start_mempoolinfo(self):
        d = threads.deferToThread(Bitcoind.getmempoolinfo)
        d.addCallback(self.getmempoolinfo_callback)

    ###########################################################################

    def getnetworkinfo_callback(self, networkinfo):
        if networkinfo:
            ms = [('network_version',     networkinfo['subversion']),
                  ('network_connections', networkinfo['connections'])]
            for tag, value in ms:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(1.0, self.start_networkinfo)

    def start_networkinfo(self):
        d = threads.deferToThread(Bitcoind.getnetworkinfo)
        d.addCallback(self.getnetworkinfo_callback)

    ###########################################################################

    def getblockchaininfo_callback(self, blockchaininfo):
        if blockchaininfo:
            ms = [('blockchain_sizeondisk', blockchaininfo['size_on_disk']),
                  ('blockchain_height',     blockchaininfo['blocks']),
                  ('blockchain_difficulty', blockchaininfo['difficulty']),
                  ('blockchain_tip_hash',   blockchaininfo['bestblockhash'])]
            for tag, value in ms:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)

    def start_blockchaininfo(self):
        d = threads.deferToThread(Bitcoind.getblockchaininfo)
        d.addCallback(self.getblockchaininfo_callback)

    ###########################################################################

    @staticmethod
    def get_tip_blockstats():
        chain_info = Bitcoind.getblockchaininfo()
        if not chain_info:
            return None
        blockheight = chain_info['blocks']
        blockhash = chain_info['bestblockhash']
        block_info = Bitcoind.getblock(blockhash)
        if not block_info:
            return None
        block_stats = Bitcoind.getblockstats(blockheight)
        if not block_stats:
            return None
        return block_stats

    def get_tip_blockstats_callback(self, block_stats):
        if block_stats:
            ms = [('tip_ntx',          block_stats['txs']),
                  ('tip_block_time',   block_stats['time']),
                  ('tip_inputs',       block_stats['ins']),
                  ('tip_outputs',      block_stats['outs']),
                  ('tip_block_weight', block_stats['total_weight']),
                  ('tip_block_size',   block_stats['total_size']),
                 ]
            for tag, value in ms:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)

    def start_tip_blockstats(self):
        d = threads.deferToThread(Bstatd.get_tip_blockstats)
        d.addCallback(self.get_tip_blockstats_callback)

    ###########################################################################


    @staticmethod
    def get_fee_rate(block):
        info = Bitcoind.estimatesmartfee(block)
        if not info:
            return None
        return info['feerate'] * 100000.0

    @staticmethod
    def get_fee_rate_eco(block):
        info = Bitcoind.estimatesmartfee_eco(block)
        if not info:
            return None
        return info['feerate'] * 100000.0

    @staticmethod
    def estimate_fees():
        fee_estimate = {b: Bstatd.get_fee_rate(b) for b in
                        FEE_RATE_BLOCKS}
        fee_estimate_eco = {b: Bstatd.get_fee_rate_eco(b) for b in
                            FEE_RATE_BLOCKS}
        return [('fee_estimates',     fee_estimate),
                ('fee_estimates_eco', fee_estimate_eco)]

    def estimatefees_callback(self, estimatefees):
        if estimatefees:
            for tag, value in estimatefees:
                message = json.dumps({tag: value}).encode("utf8")
                tag = tag.encode("utf8")
                self.publish(tag, message)
        reactor.callLater(10.0, self.start_estimatefees)

    def start_estimatefees(self):
        d = threads.deferToThread(Bstatd.estimate_fees)
        d.addCallback(self.estimatefees_callback)

    ###########################################################################

    def publish_arrive_time(self):
        info = {"last_block_arrive_time": time.time()}
        message = json.dumps(info).encode("utf8")
        tag = 'last_block_arrive_time'.encode("utf8")
        self.publish(tag, message)

    ###########################################################################

    def new_block_cb(self, block_hash):
        logging.info("block hash: %s" % block_hash)
        self.start_blockchaininfo()
        self.publish_arrive_time()
        self.start_tip_blockstats()

    def start(self):
        reactor.callLater(0.1, self.start_mempoolinfo)
        reactor.callLater(0.1, self.start_networkinfo)
        reactor.callLater(0.1, self.start_estimatefees)

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
    p = Bstatd()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
