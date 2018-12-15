#!/usr/bin/env python3

import time

from twisted.internet import reactor, threads, task

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

from tawker import Tawker
from gen_name import gen_name
from bitcoinrpc import get_block_height
from phrases import get_phrase

###############################################################################

NEW_BLOCK_QUEUE = {'running': False,
                   'queue':   [],
                  }

STATES = {'INIT', 'GETTING_BLOCK_INFO', 'OUTPUTTING'}

class NewBlock(object):
    def __init__(self, block_hash):
        self.block_info = {'hash': block_hash}
        self.state = "INIT"

    def _do_new_block(self, block_hash):
        d = threads.deferToThread(self._new_block_hash_thread, block_hash)
        d.addCallback(self.new_block_complete)

    def _speak_line_thread(self):

    def _speak_line_exec(self, block_info):
        tawker = Tawker()
        name = gen_name()
        line = 'New block: %d. I dub thee "%s."' % (height, name)
        tawker.tawk(line)
        time.sleep(0.5)
        phrase = get_phrase()
        tawker.tawk(phrase)
        return line + " " + phrase

    def new_block_hash_thread(self, block_hash):
        tawker = Tawker()
        name = gen_name()
        height = get_block_height(block_hash)
        line = 'New block: %d. I dub thee "%s."' % (height, name)
        tawker.tawk(line)
        time.sleep(0.5)
        phrase = get_phrase()
        tawker.tawk(phrase)
        return line + " " + phrase

    ###########################################################################

    def new_block_complete(self, result):
        print("complete: %s" % result)

    def _get_block_cmd_run_thread(self):

    def _get_block_cmd_start_thread(self):
        d = threads.deferToThread(self._n, block_hash)
        d.addCallback(self.new_block_complete)

    ###########################################################################

    def run(self):
        self._get_block_cmd()

    def finish():
        NEW_BLOCK_QUEUE['running'] = False
        NewBlock.try_next()

    def try_next():
        if not NEW_BLOCK_QUEUE['running'] and len(NEW_BLOCK_QUEUE['queue']) > 0:
            NEW_BLOCK_QUEUE['running'] = True
            new_block = NEW_BLOCK_QUEUE.pop()
            new_block.run()

    def listener(message):
        new_block = NewBlock(message[1].hex())
        NEW_BLOCK_QUEUE.push(new_block)
        NewBlock.try_next()

###############################################################################

def setup_zmq_block_listener(block_func):
    s = ZmqSubConnection(ZmqFactory(),
                         ZmqEndpoint("connect", "tcp://127.0.0.1:28332"))
    s.subscribe("hashblock".encode("utf-8"))
    s.messageReceived = block_func

###############################################################################

if __name__ == '__main__':
    setup_zmq_block_listener(NewBlock.listener)
    print("running reactor")
    reactor.run()
