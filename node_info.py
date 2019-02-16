import os

from twisted.internet import threads
from bitcoinrpc import Bitcoind
from lightningd import LightningDaemon

INTERVAL = 10.0

FEE_RATE_BLOCKS = [1, 3, 6, 12, 25, 50, 100, 500]

class NodeInfo(object):
    def __init__(self, reactor, screen_ui):
        self.screen_ui = screen_ui
        self.reactor = reactor

    ###########################################################################

    def _get_fee_rate(block):
        rate = Bitcoind.estimatesmartfee(block)['feerate']
        return rate * 100000.0

    def _get_fee_rate_eco(block):
        rate = Bitcoind.estimatesmartfee_eco(block)['feerate']
        return rate * 100000.0

    def _poll_node_info_thread_func():
        mempool_info = Bitcoind.getmempoolinfo()
        mempool_pct = ((mempool_info['usage'] / mempool_info['maxmempool']) *
                       100.0)
        network_info = Bitcoind.getnetworkinfo()
        fee_estimate = {b: NodeInfo._get_fee_rate(b) for b in FEE_RATE_BLOCKS}
        fee_estimate_eco = {b: NodeInfo._get_fee_rate_eco(b) for b in
                            FEE_RATE_BLOCKS}
        return {'mempool_txs':      mempool_info['size'],
                'mempool_bytes':    mempool_info['usage'],
                'mempool_percent':  mempool_pct,
                'net_connections':  network_info['connections'],
                'net_version':      network_info['subversion'],
                'fee_estimate':     fee_estimate,
                'fee_estimate_eco': fee_estimate_eco,
               }

    def _poll_node_info_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(INTERVAL, self._poll_node_info_defer)

    def _poll_node_info_defer(self):
        d = threads.deferToThread(NodeInfo._poll_node_info_thread_func)
        d.addCallback(self._poll_node_info_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(2.0, self._poll_node_info_defer)


###########################################################################

class LnNodeInfo(object):
    def __init__(self, reactor, screen_ui, lightning_rpc):
        self.screen_ui = screen_ui
        self.reactor = reactor
        self.lightning_rpc = lightning_rpc

    ###########################################################################

    def _getinfo(lightning_rpc):
        ld = LightningDaemon(lightning_rpc)
        return ld.getinfo()

    def _poll_ln_node_info_thread_func(lightning_rpc):
        info = LnNodeInfo._getinfo(lightning_rpc)
        return {'ln_version':   info['version'],
                'ln_num_peers': info['num_peers'],
                'ln_alias':     info['alias'],
               }

    def _poll_ln_node_info_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(INTERVAL, self._poll_ln_node_info_defer)

    def _poll_ln_node_info_defer(self):
        d = threads.deferToThread(LnNodeInfo._poll_ln_node_info_thread_func,
                                  self.lightning_rpc)
        d.addCallback(self._poll_ln_node_info_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(2.0, self._poll_ln_node_info_defer)
