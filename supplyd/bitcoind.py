# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import ujson
from requests import post


FEE_RATE_BLOCKS = [1, 5, 25, 50, 100, 250, 500]

class Bitcoind():
    URL = None
    HEADERS = {'content-type': 'application/json'}

    @staticmethod
    def gen_url(host='localhost', port=8332, user='rpc',
                password='bitcoinrpc'):
        return ('http://' + user + ':' + password + '@' + host + ':' +
                str(port))

    @staticmethod
    def call(method, *params):
        #session = requests.Session()
        payload = {'method': method,
                   'params': list(params),
                   'jsonrpc': "2.0"}
        try:
            r = post(Bitcoind.URL, headers=Bitcoind.HEADERS,
                     data=ujson.dumps(payload))
        except Exception as e:
            print(e)
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

    @staticmethod
    def getblock(block_hash):
        return Bitcoind.call('getblock', block_hash)

    @staticmethod
    def gettxoutsetinfo():
        return Bitcoind.call('gettxoutsetinfo')

    @staticmethod
    def getblockstats(height):
        return Bitcoind.call('getblockstats', height)

    @staticmethod
    def getblock_raw(block_hash):
        return Bitcoind.call('getblock', block_hash, 0)

    @staticmethod
    def getblock_json(block_hash):
        return Bitcoind.call('getblock', block_hash, 2)

    @staticmethod
    def gettx_json(txid):
        return Bitcoind.call('getrawtransaction', txid, 1)

    @staticmethod
    def getmempoolinfo():
        return Bitcoind.call('getmempoolinfo')

    @staticmethod
    def getblockchaininfo():
        return Bitcoind.call('getblockchaininfo')

    @staticmethod
    def getnetworkinfo():
        return Bitcoind.call('getnetworkinfo')

    @staticmethod
    def getblockhash(height):
        return hod

    @staticmethod
    def estimatesmartfee(block):
        return Bitcoind.call('estimatesmartfee', block)

    @staticmethod
    def estimatesmartfee_eco(block):
        return Bitcoind.call('estimatesmartfee', block, "ECONOMICAL")
