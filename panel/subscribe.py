# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import json
import logging

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection

PRICE_TAGS = ['price_btccad']
BSTAT_TAGS = ['blockchain_tip_hash',
              'blockchain_height',
              'blockchain_difficulty',
              'mempool_txes',
              'mempool_bytes',
              'mempool_mem_used',
              'mempool_mem_max',
              'network_version',
              'network_connections',
              'fee_estimates',
              'fee_estimates_eco',
              'last_block_arrive_time',
              'tip_ntx',
              'tip_block_time',
              'tip_inputs',
              'tip_outputs',
              'tip_block_weight',
              'tip_block_size']
CSTAT_TAGS = ['ip_addr',
              'cpu_pct',
              'mem_total',
              'mem_used',
              'mem_used_pct']

class Subscribe():
    def __init__(self, config, info):
        self.config = config
        self.info = info


        self.zmq_factory = ZmqFactory()

        price_endpoint = config['Panel']['ZmqSubPriceEndpoint']
        price_endpoint = ZmqEndpoint(ZmqEndpointType.connect, price_endpoint)
        connection = ZmqSubConnection(self.zmq_factory, price_endpoint)
        connection.gotMessage = self.update_info
        for tag in PRICE_TAGS:
            connection.subscribe(tag.encode("utf8"))

        bstat_endpoint = config['Panel']['ZmqSubBstatEndpoint']
        bstat_endpoint = ZmqEndpoint(ZmqEndpointType.connect, bstat_endpoint)
        connection = ZmqSubConnection(self.zmq_factory, bstat_endpoint)
        connection.gotMessage = self.update_info
        for tag in BSTAT_TAGS:
            connection.subscribe(tag.encode("utf8"))

        cstat_endpoint = config['Panel']['ZmqSubCstatEndpoint']
        cstat_endpoint = ZmqEndpoint(ZmqEndpointType.connect, cstat_endpoint)
        connection = ZmqSubConnection(self.zmq_factory, cstat_endpoint)
        connection.gotMessage = self.update_info
        for tag in CSTAT_TAGS:
            connection.subscribe(tag.encode("utf8"))

    def update_info(self, message, tag):
        info = json.loads(message.decode("utf8"))
        tag = tag.decode("utf8")
        logging.info("got: %s" % info)
        if tag not in info:
            logging.error("malformed message")
        self.info.update_info(tag, info[tag])
