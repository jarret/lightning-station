#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import time
import argparse
import logging
import traceback


from twisted.internet import reactor, task

from screen_ui import ScreenUI
from bitcoinrpc import Bitcoind
from logger import setup_logging
from block_listener import NewBlockQueue
from system_resources import SystemResources
from audio_player import AudioPlayer
from jukebox import Jukebox
from node_info import NodeInfo, LnNodeInfo


###############################################################################

class PeriodicUpdates(object):
    def __init__(self, sui):
        self.start_time = time.time()
        self.sui = sui

    def _update_time(self):
        self.sui.update_info({'current_time': time.time()})

    def run(self):
        t = task.LoopingCall(self._update_time)
        t.start(5.0)


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
    setup_logging(args.log_file, 'jukebox', min_level=logging.INFO,
                  console_silent=(not args.console))

    assert os.path.exists(args.audio_dir), "audio dir doesn't exist?"
    assert os.path.isdir(args.audio_dir), "audio dir not a dir?"
    assert os.path.exists(args.lightning_rpc), "rpc file doesn't exist?"
    assert os.path.exists("/dev/" + args.blockchain_device), ("device doesn't "
                                                              "exist?")
    assert os.path.exists(args.blockchain_dir), "blockchain dir doesn't exist?"
    assert os.path.isdir(args.blockchain_dir), "blockchain dir not a dir?"

    r = reactor
    # setup urwid screen output
    sui = ScreenUI(r, args.console)
    # listen on ZMQ for new blocks
    bc_info = Bitcoind.getblockchaininfo()
    block_hash = bc_info['bestblockhash'] if bc_info else None
    queue = NewBlockQueue(r, sui, AudioPlayer(), block_hash)
    # start periodic timers
    pu = PeriodicUpdates(sui)
    r.callLater(0.5, pu.run)

    sr = SystemResources(r, sui, args.blockchain_dir, args.blockchain_device)
    sr.run()

    ni = NodeInfo(r, sui)
    ni.run()

    lni = LnNodeInfo(r, sui, args.lightning_rpc)
    lni.run()

    j = Jukebox(r, sui, args.audio_dir, args.lightning_rpc)
    j.run()

    if args.websocket:
        from serve_web import ServeWeb
        from serve_websocket import ServeWebsocket
        from web_eink_ui import WebEinkUI
        weui = WebEinkUI()
        sw = ServeWeb(r)
        sw.run()
        sws = ServeWebsocket(r, sui, weui, j)
        sws.run()
    else:
        from physical_ui import PhysicalUI
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
        logging.error(tb)
