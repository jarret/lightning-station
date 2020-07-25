# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import logging
from twisted.internet import threads
from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection

from bitcoinrpc import Bitcoind
from gen_name import gen_block_name
from phrases import get_phrase
from tawker import Tawker

################################################################################

class NewBlock(object):
    def __init__(self, new_block_queue, block_hash, screen_ui, audio_player):
        self.new_block_queue = new_block_queue
        self.block_hash = block_hash
        self.screen_ui = screen_ui
        self.arrival_time = time.time()
        self.audio_player = audio_player

    ###########################################################################

    def _speak_line_thread_func_annoying(height, name, phrase):
        #logging.info("speak thread func")
        tawker = Tawker()
        line = 'New block: %d. I dub thee "%s."' % (height, name)
        time.sleep(0.5)
        tawker.tawk(line)
        time.sleep(0.3)
        tawker.tawk(phrase)
        return line + " " + phrase

    def _speak_line_thread_func(height, name, phrase):
        tawker = Tawker()
        time.sleep(1.0)
        line = 'New block: %d' % height
        tawker.tawk(line)
        logging.info("speak: %s" % line)
        #time.sleep(0.3)
        #tawker.tawk(phrase)
        return line

    def _speak_line_callback(self, result):
        #logging.info("spoke line: %s" % result)
        self.new_block_queue.finish_block()

    def _speak_line_defer(self, info):
        #logging.info("speak defer")
        d = threads.deferToThread(NewBlock._speak_line_thread_func,
                                  info['block_height'],
                                  info['block_name'],
                                  info['block_phrase'])
        d.addCallback(self._speak_line_callback)
        logging.info("sound effect")
        self.audio_player.play_sound_effect('block')

    ###########################################################################

    def _getblock_cmd_thread_func(block_hash):
        #logging.info("getblock thread func")
        info = Bitcoind.getblock(block_hash)
        raw = Bitcoind.getblock_raw(block_hash)
        info['raw'] = raw
        info['name'] = gen_block_name(block_hash)
        info['phrase'] = get_phrase()
        return info

    def _getblock_cmd_callback(self, result):
        #logging.info("getblock callback")
        info = {'block_arrival_time': self.arrival_time,
                'block_name':         result['name'],
                'block_phrase':       result['phrase'],
                'block_height':       result['height'],
                'block_n_txes':       result['nTx'],
                'block_size':         result['size'],
                'block_weight':       result['weight'],
                'block_timestamp':    result['time'],
               }
        self._speak_line_defer(info)
        self.screen_ui.update_info(info)

    def _getblock_cmd_defer(self):
        #logging.info("getblock defer")
        d = threads.deferToThread(NewBlock._getblock_cmd_thread_func,
                                  self.block_hash)
        d.addCallback(self._getblock_cmd_callback)

    ###########################################################################

    def run(self):
        #logging.info("run")
        self._getblock_cmd_defer()

################################################################################

class NewBlockQueue(object):
    """ New blocks that arrive are notified to us from bitcoind via ZeroMQ.
        They are queued up for handling since they can arrive faster than
        they are able to be handled.
    """
    def __init__(self, reactor, screen_ui, audio_player, first_block_hash):
        f = ZmqFactory()
        f.reactor = reactor
        e = ZmqEndpoint("connect", "tcp://127.0.0.1:28332")
        s = ZmqSubConnection(f, e)
        s.subscribe("hashblock".encode("utf-8"))
        s.messageReceived = self.listener
        self.screen_ui = screen_ui
        self.new_block_queue = []
        self.queue_running = False
        self.audio_player = audio_player

        new_block = NewBlock(self, first_block_hash, self.screen_ui,
                             audio_player)
        self.new_block_queue.append(new_block)
        self._try_next()

    def finish_block(self):
        #logging.info("finish")
        self.queue_running = False
        self._try_next()

    def _try_next(self):
        if (self.queue_running == False) and (len(self.new_block_queue) > 0):
            self.queue_running = True
            new_block = self.new_block_queue.pop(0)
            new_block.run()

    def listener(self, message):
        new_block = NewBlock(self, message[1].hex(), self.screen_ui,
                             self.audio_player)
        self.new_block_queue.append(new_block)
        self._try_next()
