#!/usr/bin/env python3

import time
import argparse
import logging


from twisted.internet import reactor, task

from ip_address import get_ip_address
from screen_ui import ScreenUI
from bitcoinrpc import Bitcoind
from logger import log, setup_log
from serve_web import ServeWeb
from serve_websocket import ServeWebsocket
from block_listener import NewBlockQueue
from eink_ui import EinkUI
from system_resources import SystemResources


###############################################################################

FEE_RATE_BLOCKS = [1, 3, 6, 12, 24, 48, 100, 500]

class NodeInfo(object):

    def get_fee_rate(block):
        rate = Bitcoind.estimatesmartfee(block)['feerate']
        return rate * 100000.0

    def get_fee_rate_eco(block):
        rate = Bitcoind.estimatesmartfee_eco(block)['feerate']
        return rate * 100000.0

    def fetch():
        mempool_info = Bitcoind.getmempoolinfo()
        mempool_pct = ((mempool_info['usage'] / mempool_info['maxmempool']) *
                       100.0)
        network_info = Bitcoind.getnetworkinfo()
        fee_estimate = {b: NodeInfo.get_fee_rate(b) for b in FEE_RATE_BLOCKS}
        fee_estimate_eco = {b: NodeInfo.get_fee_rate_eco(b) for b in
                            FEE_RATE_BLOCKS}
        return {'mempool_txs':      mempool_info['size'],
                'mempool_bytes':    mempool_info['usage'],
                'mempool_percent':  mempool_pct,
                'net_connections':  network_info['connections'],
                'net_version':      network_info['subversion'],
                'fee_estimate':     fee_estimate,
                'fee_estimate_eco': fee_estimate_eco,
               }

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
        self.sui.update_info({'current_time': time.time()})

    def _update_node_info(self):
        node_info = NodeInfo.fetch()
        self.sui.update_info(node_info)

    def _update_host_info(self):
        host_info = HostInfo.fetch()
        self.sui.update_info(host_info)

    def run(self):
        t = task.LoopingCall(self._update_time)
        t.start(1.0)

        l = task.LoopingCall(self._update_node_info)
        l.start(5.0)

        l = task.LoopingCall(self._update_host_info)
        l.start(20.0)


###############################################################################

DEFAULT_LOG_FILE = "/tmp/lightning-station.log"

DESCRIPTION = ("Lighting Station - monitors and doodads for a bitcoin full "
               "node, lightning node and stuff that is fun and interesting.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--console', action='store_true',
                        help="print info to console log instead of fancy "
                             "curses output")
    parser.add_argument('-l', '--log-file', type=str, default=DEFAULT_LOG_FILE,
                        help="File to write debug logging blabber to; Best to "
                             "keep off of Pi's SD card.")
    args = parser.parse_args()
    setup_log(args.console, args.log_file)

    log("hello")

    r = reactor
    # setup urwid screen output
    sui = ScreenUI(r, args.console)
    # listen on ZMQ for new blocks
    queue = NewBlockQueue(r, sui,
                          Bitcoind.getblockchaininfo()['bestblockhash'])
    # start periodic timers
    pu = PeriodicUpdates(sui)
    r.callLater(0.5, pu.run)

    sr = SystemResources(r, sui)
    sr.run()

    eui = EinkUI()

    sw = ServeWeb(r)
    sw.run()

    sws = ServeWebsocket(r, sui, eui)
    sws.run()

    try:
        if args.console:
            r.run()
        else:
            # reactor is sarted from screen_ui
            sui.start_event_loop()
    except:
        sui.stop()
        logging.exception('')
