#!/usr/bin/env python3

import urwid
import time

from twisted.internet import reactor, threads, task

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

from tawker import Tawker
from gen_name import gen_block_name
from bitcoinrpc import Bitcoind
from phrases import get_phrase
from ip_address import get_ip_address
from screen_ui import ScreenUI

from block_listener import NewBlockQueue


###############################################################################

class NodeInfo(object):
    def fetch():
        info = {}
        info['mempool'] = Bitcoind.getmempoolinfo()
        info['network'] = Bitcoind.getnetworkinfo()
        info['fee_estimate'] = {1:   Bitcoind.estimatesmartfee(1),
                                3:   Bitcoind.estimatesmartfee(3),
                                6:   Bitcoind.estimatesmartfee(6),
                                12:  Bitcoind.estimatesmartfee(12),
                                24:  Bitcoind.estimatesmartfee(24),
                                48:  Bitcoind.estimatesmartfee(48),
                                100: Bitcoind.estimatesmartfee(100),
                                500: Bitcoind.estimatesmartfee(500)
                               }
        return info

class HostInfo(object):
    def fetch():
        info = {}
        info['ip_address'] = get_ip_address()
        return info

###############################################################################

class PeriodicUpdates(object):
    def __init__(self, sui):
        self.start_time = time.time()
        self.sui = sui

    def _update_time(self):
        elapsed = time.time() - self.start_time
        self.sui.update_info({'elapsed': elapsed})

    def _update_node_info(self):
        node_info = NodeInfo.fetch()
        self.sui.update_info(node_info)

    def _update_host_info(self):
        host_info = HostInfo.fetch()
        self.sui.update_info(host_info)

    def run(self):
        t = task.LoopingCall(self._update_time)
        t.start(1.0, now=False)

        l = task.LoopingCall(self._update_node_info)
        l.start(2.0, now=False)

        l = task.LoopingCall(self._update_host_info)
        l.start(3.0, now=False)


###############################################################################

if __name__ == '__main__':
    r = reactor

    # setup urwid screen output
    sui = ScreenUI(r)

    # listen on ZMQ for new blocks
    queue = NewBlockQueue(r, sui)

    # start periodic timers
    pu = PeriodicUpdates(sui)
    pu.run()
    # runs reactor:
    sui.run()
