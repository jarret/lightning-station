# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import ujson
import requests
from requests import post

class Bitcoind():
    def __init__(self, host='localhost', port=8332, user='bitcoinrpc',
                 password='rpc'):
        self.url = ('http://' + user + ':' + password + '@' + host + ':' +
                    str(port))
        self.headers = {'content-type': 'application/json'}

    def call(self, method, *params):
        #session = requests.Session()
        payload = {'method': method,
                   'params': list(params),
                   'jsonrpc': "2.0"}
        try:
            #r = session.post(self.url, headers=self.headers,
            #                 data=ujson.dumps(payload))
            r = post(self.url, headers=self.headers,
                     data=ujson.dumps(payload))
        except:
            return None
        if not r.status_code in {200, 500}:
            return None
        try:
            return ujson.loads(r.text)['result']
            #return r.json()['result']
        except:
            return None

    def getblock(self, block_hash):
        return self.call('getblock', block_hash)

    def getblock_raw(self, block_hash):
        return self.call('getblock', block_hash, 0)

    def getblock_json(self, block_hash):
        return self.call('getblock', block_hash, 2)

    def gettx_json(self, txid):
        return self.call('getrawtransaction', txid, 1)

    def getmempoolinfo(self):
        return self.call('getmempoolinfo')

    def getblockchaininfo(self):
        return self.call('getblockchaininfo')

    def getnetworkinfo(self):
        return self.call('getnetworkinfo')



class StaticBitcoind():
    URL = None
    HEADERS = {'content-type': 'application/json'}

    def gen_url(host='localhost', port=8332, user='bitcoinrpc',
                password='rpc'):
        return ('http://' + user + ':' + password + '@' + host + ':' +
                str(port))

    def call(method, *params):
        #session = requests.Session()
        payload = {'method': method,
                   'params': list(params),
                   'jsonrpc': "2.0"}
        try:
            #r = session.post(StaticBitcoind.URL,
            #                 headers=StaticBitcoind.HEADERS,
            #                 data=ujson.dumps(payload))
            r = post(StaticBitcoind.URL, headers=StaticBitcoind.HEADERS,
                     data=ujson.dumps(payload))
        except:
            print("1")
            return None
        if not r.status_code in {200, 500}:
            print("2")
            return None
        try:
            return ujson.loads(r.text)['result']
            #return r.json()['result']
        except:
            print("3")
            return None

    def getblock(block_hash):
        return StaticBitcoind.call('getblock', block_hash)

    def getblock_raw(block_hash):
        return StaticBitcoind.call('getblock', block_hash, 0)

    def getblock_json(block_hash):
        return StaticBitcoind.call('getblock', block_hash, 2)

    def gettx_json(txid):
        return StaticBitcoind.call('getrawtransaction', txid, 1)

    def getmempoolinfo():
        return StaticBitcoind.call('getmempoolinfo')

    def getblockchaininfo():
        return StaticBitcoind.call('getblockchaininfo')

    def getnetworkinfo():
        return StaticBitcoind.call('getnetworkinfo')

    def getblockhash(height):
        return StaticBitcoind.call('getblockhash', height)



