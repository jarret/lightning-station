# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import logging

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import  ZmqSubConnection

class BlockListener():
    def __init__(self, config, new_block_cb):
        self.new_block_cb = new_block_cb
        sub_endpoint = config['Bstatd']['ZmqSubBlockHashEndpoint']
        f = ZmqFactory()
        e = ZmqEndpoint(ZmqEndpointType.connect, sub_endpoint)
        s = ZmqSubConnection(f, e)
        s.subscribe("hashblock".encode("utf-8"))
        s.messageReceived = self.msg_recv

    def msg_recv(self,  message):
        h = message[1].hex()
        logging.info("block: %s" % h)
        self.new_block_cb(h)


