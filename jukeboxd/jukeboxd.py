#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import time
import argparse
import logging
import traceback

from configparser import ConfigParser

from twisted.internet import reactor, task

from physical_ui import PhysicalUI
from logger import setup_logging
from audio_player import AudioPlayer
from jukebox import Jukebox


###############################################################################

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".jukebox")
CONFIG_FILE = os.path.join(CONFIG_DIR, "jukebox.conf")
if not os.path.exists(CONFIG_FILE):
    sys.exit("*** could not find %s" % CONFIG_FILE)
config = ConfigParser()
config.read(CONFIG_FILE)

LOG_FILE = os.path.join(CONFIG_DIR, "jukeboxd.log")
setup_logging(LOG_FILE, "jukeboxd", console_silent=True,
              min_level=logging.DEBUG)


if __name__ == '__main__':
    j = Jukebox(config)
    pui = PhysicalUI(config, j)
    ap = AudioPlayer(config)

    try:
        reactor.run()
    except Exception:
        tb = traceback.format_exc()
        logging.error(tb)
