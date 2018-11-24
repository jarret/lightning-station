#!/usr/bin/env python3

import os
import json
import time
import subprocess

PRODUCTION = False

TEST_AUDIO = {
    'rickroll':  {'path': '/home/jarret/audio/rickroll.mp3'},
    'yousuffer': {'path': '/home/jarret/audio/yousuffer.wav'},
}
DEPLOY_AUDIO = {
    'rickroll':  {'path': '/home/pi/btc-rust/audio/rickroll.mp3'},
    'yousuffer': {'path': '/home/pi/btc-rust/audio/yousuffer.wav'},
}

AUDIO = DEPLOY_AUDIO if PRODUCTION else TEST_AUDIO

TEST_PLAY = ['echo', 'omxplayer']
DEPLOY_PLAY = ['omxplayer']

PLAY = DEPLOY_PLAY if PRODUCTION else TEST_PLAY

TEST_BLOCK = ['echo', '{\"headers\": 123}']
DEPLOY_BLOCK = ['/home/pi/btc-rust/bitcoind-run/cli.sh', "getblockchaininfo"]

BLOCK = DEPLOY_BLOCK if PRODUCTION else TEST_BLOCK


class Monitor(object):
    def __init__(self):
        self.block = 0
        self.sound_path = AUDIO['yousuffer']['path']

    def query_block(self):
        info = json.loads(subprocess.check_output(BLOCK).decode('utf-8'))
        return info['headers']

    def play_sound(self):
        subprocess.call(PLAY + [self.sound_path])

    def cycle(self):
        time.sleep(3)
        block = self.query_block()
        print("got block: %s" % block)
        if block != self.block:
            print("new block!")
            self.play_sound()
            self.block = block

    def run(self):
        while True:
            self.cycle()


if __name__ == '__main__':
    #for aid, info in AUDIO.items():
    #    print("aid: %s" % aid)
    #    assert os.path.exists(info['path'])
    m = Monitor()
    print("running")
    m.run()

