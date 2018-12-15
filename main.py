#!/usr/bin/env python3

import time

from twisted.internet import reactor, threads, task

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

from tawker import Tawker
from gen_name import gen_name
from bitcoinrpc import get_block_height
from phrases import get_phrase

###############################################################################

def new_block_hash(block_hash):
    tawker = Tawker()
    name = gen_name()
    height = get_block_height(block_hash)
    line = 'New block: %d. I dub thee "%s."' % (height, name)
    tawker.tawk(line)
    time.sleep(0.5)
    phrase = get_phrase()
    tawker.tawk(phrase)
    return line + " " + phrase

def new_block_complete(result):
    print("complete: %s" % result)

def do_new_block(block_hash):
    d = threads.deferToThread(new_block_hash, block_hash)
    d.addCallback(new_block_complete)

###############################################################################

zf = ZmqFactory()
e = ZmqEndpoint("connect", "tcp://127.0.0.1:28332")

s = ZmqSubConnection(zf, e)
s.subscribe("hashblock".encode("utf-8"))

def new_block(message):
    print(message)
    h = message[1].hex()
    print(h)
    do_new_block(h)

s.messageReceived = new_block

###############################################################################

print("running reactor")
reactor.run()
