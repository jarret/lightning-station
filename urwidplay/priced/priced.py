#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import json

from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from twisted.internet import threads

from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory
from txzmq import ZmqSubConnection, ZmqPubConnection


import krakenex

class Kraken():
    def fetch_btccad():
        k = krakenex.API()
        ticker = k.query_public('Ticker', {'pair': 'XXBTZCAD'})
        last_close_raw = ticker["result"]["XXBTZCAD"]["c"]
        last_close = last_close_raw[0]
        return last_close


PUBLISH_ENDPOINT = "tcp://127.0.0.1:7788"

class Priced(Service):
    def __init__(self):
        factory = ZmqFactory()
        pub_endpoint = ZmqEndpoint(ZmqEndpointType.bind, PUBLISH_ENDPOINT)
        self.pub_connection = ZmqPubConnection(factory, pub_endpoint)

    def publish_price(self, tag, price_info):
        msg = json.dumps(price_info).encode("utf8")
        self.pub_connection.publish(msg, tag=tag)


    def fetch_btccad_callback(self, btccad):
        print("price: %0.2f" % float(btccad))
        reactor.callLater(10.0, self.start_fetch_thread)

    def start_fetch_thread(self):
        d = threads.deferToThread(Kraken.fetch_btccad)
        d.addCallback(self.fetch_btccad_callback)


    def start(self):
        reactor.callLater(0.1, self.start_fetch_thread)

    def stop(self):
        pass

    def startService(self):
        super().startService()
        self.start()

    def stopService(self):
        super().stopService()
        self.stop()
        time.sleep(0.5)
        reactor.stop()

if __name__ == "__main__":
    p = Priced()
    p.start()
    reactor.addSystemEventTrigger("before", "shutdown", p.stop)
    reactor.run()
