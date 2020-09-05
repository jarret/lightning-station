# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import requests
import json
import logging
import traceback

RPC_PORT = 8332
RPC_USER = 'rpc'
RPC_PASSWORD = 'bitcoinrpc'

URL = 'http://' + RPC_USER + ':' + RPC_PASSWORD + '@localhost:' + str(RPC_PORT)

###############################################################################

class RPCHost(object):
    def __init__(self):
        self._session = requests.Session()
        self._url = URL
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod,
                              "params": list(params), "jsonrpc": "2.0"})
        response = self._session.post(self._url, headers=self._headers,
                                      data=payload)
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' +
                            str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']


###############################################################################


class Bitcoind(object):
    def rpc(*args):
        host = RPCHost()
        try:
            return host.call(*args)
        except Exception as e:
            #print(e)
            #print(traceback.format_exc())
            return None

    def getblock(block_hash):
        return Bitcoind.rpc('getblock', block_hash)

    def getblock_raw(block_hash):
        return Bitcoind.rpc('getblock', block_hash, 0)

    def getmempoolinfo():
        return Bitcoind.rpc('getmempoolinfo')

    def getblockchaininfo():
        return Bitcoind.rpc('getblockchaininfo')

    def getnetworkinfo():
        return Bitcoind.rpc('getnetworkinfo')

    def estimatesmartfee(blocks):
        return Bitcoind.rpc('estimatesmartfee', blocks)

    def estimatesmartfee_eco(blocks):
        return Bitcoind.rpc('estimatesmartfee', blocks, "ECONOMICAL")

    def get_parsed_tx(txid):
        raw = Bitcoind.rpc('getrawtransaction', txid)
        if not raw:
            return None
        return Bitcoind.rpc('decoderawtransaction', raw)

