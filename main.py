#!/usr/bin/env python3

import os
import time
import argparse
import logging
import traceback


from twisted.internet import reactor, task

from ip_address import get_ip_address
from screen_ui import ScreenUI
from bitcoinrpc import Bitcoind
from logger import log, setup_log
from serve_web import ServeWeb
from serve_websocket import ServeWebsocket
from block_listener import NewBlockQueue
from web_eink_ui import WebEinkUI
from physical_ui import PhysicalUI
from system_resources import SystemResources
from audio_player import AudioPlayer
from jukebox import Jukebox


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
        t.start(5.0)

        l = task.LoopingCall(self._update_node_info)
        l.start(10.0)

        l = task.LoopingCall(self._update_host_info)
        l.start(20.0)


###############################################################################

DEFAULT_LOG_FILE = "/tmp/lightning-station.log"

DESCRIPTION = ("Lightning Station - monitors and doodads for a bitcoin full "
               "node, lightning node and stuff that is fun and interesting.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--console', action='store_true',
                        help="print info to console log instead of fancy "
                             "curses output")
    parser.add_argument('-w', '--websocket', action='store_true',
                        help="present UI through websocket rather than e-ink")
    parser.add_argument('-l', '--log-file', type=str, default=DEFAULT_LOG_FILE,
                        help="File to write debug logging blabber to; Best to "
                             "keep off of Pi's SD card.")
    parser.add_argument('audio_dir', type=str,
                        help="directory wth the mp3 songs in it")
    parser.add_argument('lightning_rpc', type=str,
                        help="c-lightning daemon rpc file")
    parser.add_argument('blockchain_device', type=str,
                        help="device holding the blockchain for monitoring I/O")
    parser.add_argument('blockchain_dir', type=str,
                        help="dir holding the blockchain for monitoring size")
    args = parser.parse_args()
    setup_log(args.console, args.log_file)

    assert os.path.exists(args.audio_dir), "audio dir doesn't exist?"
    assert os.path.isdir(args.audio_dir), "audio dir not a dir?"
    assert os.path.exists(args.lightning_rpc), "rpc file doesn't exist?"
    assert os.path.exists("/dev/" + args.blockchain_device), ("device doesn't "
                                                              "exist?")
    assert os.path.exists(args.blockchain_dir), "blockchain dir doesn't exist?"
    assert os.path.isdir(args.blockchain_dir), "blockchain dir not a dir?"
    log("hello")

    r = reactor
    # setup urwid screen output
    sui = ScreenUI(r, args.console)
    # listen on ZMQ for new blocks
    queue = NewBlockQueue(r, sui, AudioPlayer(),
                          Bitcoind.getblockchaininfo()['bestblockhash'])
    # start periodic timers
    pu = PeriodicUpdates(sui)
    r.callLater(0.5, pu.run)

    sr = SystemResources(r, sui, args.blockchain_dir, args.blockchain_device)
    sr.run()


    j = Jukebox(r, sui, args.audio_dir, args.lightning_rpc)
    j.run()

    if args.websocket:
        weui = WebEinkUI()
        sw = ServeWeb(r)
        sw.run()
        sws = ServeWebsocket(r, sui, weui, j)
        sws.run()
     else:
        pui = PhysicalUI(r, sui, j)
        pui.run()

    try:
        if args.console:
            r.run()
        else:
            # reactor is sarted from screen_ui
            sui.start_event_loop()
    except Exception:
        sui.stop()
        tb = traceback.format_exc()
        log(tb)
