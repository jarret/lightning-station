# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import sys
from twisted.internet import threads

from bitcoind import Bitcoind
from block_stats import BlockStats

class ExecGrind():

    @staticmethod
    def grindthread(height):
        block_hash = Bitcoind.getblockhash(height)
        bs = BlockStats(block_hash)
        #print("running.. %d" % height)
        return bs.run()

    def grindthread_cb(self, result, height, cb):
        #print("grindthread result: %s" % result)
        cb(height, result)

    def run(self, height, cb):
        print("running @ %d" % height)
        d = threads.deferToThread(ExecGrind.grindthread, height)
        d.addCallback(self.grindthread_cb, height, cb)
        pass
