import time
import requests
import json

RPC_PORT = 8332
RPC_USER = 'bitcoinrpc'
RPC_PASSWORD = 'rpc'

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
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url,
                    headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception("Failed to connect for remote procedure "
                                    "call.")
                hadFailedConnections = True
                log("Couldn't connect for remote procedure call, will "
                    "sleep for five seconds and then try again ({} more "
                    "tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    log('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' +
                            str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']


###############################################################################


class Bitcoind(object):
    def getblock(block_hash):
        host = RPCHost()
        return host.call('getblock', block_hash)

    def getblock_raw(block_hash):
        host = RPCHost()
        return host.call('getblock', block_hash, 0)

    def getmempoolinfo():
        host = RPCHost()
        return host.call('getmempoolinfo')

    def getblockchaininfo():
        host = RPCHost()
        return host.call('getblockchaininfo')

    def getnetworkinfo():
        host = RPCHost()
        return host.call('getnetworkinfo')

    def estimatesmartfee(blocks):
        host = RPCHost()
        return host.call('estimatesmartfee', blocks)

    def get_parsed_tx(txid):
        host = RPCHost()
        raw = host.call('getrawtransaction', txid)
        return host.call('decoderawtransaction', raw)

