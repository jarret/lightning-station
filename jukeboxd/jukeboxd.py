#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import time
import argparse
import logging
import traceback

from twisted.internet import reactor, task

from physical_ui import PhysicalUI
from logger import setup_logging
from audio_player import AudioPlayer
from jukebox import Jukebox


###############################################################################

DEFAULT_LOG_FILE = "/tmp/lightning-station.log"

DESCRIPTION = ("Lightning Station - monitors and doodads for a bitcoin full "
               "node, lightning node and stuff that is fun and interesting.")

if __name__ == '__main__':
    j = Jukebox(reactor, sui, args.audio_dir, args.lightning_rpc)
    pui = PhysicalUI(r, sui, j)
    ap = AudioPlayer(r, sui, j)

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
