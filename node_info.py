import os

from twisted.internet import threads
from bitcoinrpc import Bitcoind
from lightningd import LightningDaemon

FEE_RATE_BLOCKS = [1, 5, 25, 50, 100, 250, 500]

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

    ###########################################################################

    def _poll_fee_est_thread_func():
        fee_estimate = {b: NodeInfo._get_fee_rate(b) for b in FEE_RATE_BLOCKS}
        fee_estimate_eco = {b: NodeInfo._get_fee_rate_eco(b) for b in
                            FEE_RATE_BLOCKS}
        return {'fee_estimate':     fee_estimate,
                'fee_estimate_eco': fee_estimate_eco,
               }

    def _poll_fee_est_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(10.0, self._poll_fee_est_defer)

    def _poll_fee_est_defer(self):
        d = threads.deferToThread(NodeInfo._poll_fee_est_thread_func)
        d.addCallback(self._poll_fee_est_callback)

    ###########################################################################

    def _poll_network_thread_func():
        network_info = Bitcoind.getnetworkinfo()
        return {'net_connections':  network_info['connections'],
                'net_version':      network_info['subversion'],
               }

    def _poll_network_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(10.0, self._poll_network_defer)

    def _poll_network_defer(self):
        d = threads.deferToThread(NodeInfo._poll_network_thread_func)
        d.addCallback(self._poll_network_callback)

    ###########################################################################

    def _poll_mempool_thread_func():
        mempool_info = Bitcoind.getmempoolinfo()
        mempool_pct = ((mempool_info['usage'] / mempool_info['maxmempool']) *
                       100.0)
        return {'mempool_txs':      mempool_info['size'],
                'mempool_bytes':    mempool_info['usage'],
                'mempool_max':      mempool_info['maxmempool'],
                'mempool_percent':  mempool_pct,
               }

    def _poll_mempool_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(1.0, self._poll_mempool_defer)

    def _poll_mempool_defer(self):
        d = threads.deferToThread(NodeInfo._poll_mempool_thread_func)
        d.addCallback(self._poll_mempool_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(2.0, self._poll_mempool_defer)
        self.reactor.callLater(2.0, self._poll_network_defer)
        self.reactor.callLater(2.0, self._poll_fee_est_defer)


###########################################################################

NODES_INTERVAL = 5.0
FUNDS_INTERVAL = 1.0
INFO_INTERVAL = 1.0

class LnNodeInfo(object):
    def __init__(self, reactor, screen_ui, lightning_rpc):
        self.screen_ui = screen_ui
        self.reactor = reactor
        self.lightning_rpc = lightning_rpc

    ###########################################################################

    def _getnodes(lightning_rpc):
        ld = LightningDaemon(lightning_rpc)
        return ld.listnodes()

    def _sum_nodes(nodes):
        return len(nodes['nodes'])

    def _poll_ln_nodes_thread_func(lightning_rpc):
        return {'ln_node_peers': 10}
        #nodes = LnNodeInfo._getnodes(lightning_rpc)
        #n_nodes = LnNodeInfo._sum_nodes(nodes)
        #return {'ln_node_peers': n_nodes,
        #       }

    def _poll_ln_nodes_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(NODES_INTERVAL, self._poll_ln_nodes_defer)

    def _poll_ln_nodes_defer(self):
        d = threads.deferToThread(LnNodeInfo._poll_ln_nodes_thread_func,
                                  self.lightning_rpc)
        d.addCallback(self._poll_ln_nodes_callback)

    ###########################################################################

    def _sum_funds(funds):
        chain = sum(int(o['amount_msat']) for o in funds['outputs'])
        total = sum(int(c['amount_msat']) for c in funds['channels'])
        ours = sum(int(c['our_amount_msat']) for c in funds['channels'])
        theirs = total - ours
        return theirs, ours, chain

    def _getfunds(lightning_rpc):
        ld = LightningDaemon(lightning_rpc)
        return ld.listfunds()

    def _poll_ln_funds_thread_func(lightning_rpc):
        funds = LnNodeInfo._getfunds(lightning_rpc)
        theirs, ours, chain = LnNodeInfo._sum_funds(funds)
        return {'ln_channel_ours':   ours,
                'ln_channel_theirs': theirs,
                'ln_channel_chain':  chain,
               }

    def _poll_ln_funds_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(FUNDS_INTERVAL, self._poll_ln_funds_defer)

    def _poll_ln_funds_defer(self):
        d = threads.deferToThread(LnNodeInfo._poll_ln_funds_thread_func,
                                  self.lightning_rpc)
        d.addCallback(self._poll_ln_funds_callback)

    ###########################################################################

    def _getinfo(lightning_rpc):
        ld = LightningDaemon(lightning_rpc)
        return ld.getinfo()

    def _poll_ln_node_info_thread_func(lightning_rpc):
        info = LnNodeInfo._getinfo(lightning_rpc)
        return {'ln_version':           info['version'],
                'ln_inet_peers':        info['num_peers'],
                'ln_alias':             info['alias'],
                'ln_channels_pending':  info['num_pending_channels'],
                'ln_channels_active':   info['num_active_channels'],
                'ln_channels_inactive': info['num_inactive_channels'],
               }

    def _poll_ln_node_info_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(INFO_INTERVAL, self._poll_ln_node_info_defer)

    def _poll_ln_node_info_defer(self):
        d = threads.deferToThread(LnNodeInfo._poll_ln_node_info_thread_func,
                                  self.lightning_rpc)
        d.addCallback(self._poll_ln_node_info_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(2.0, self._poll_ln_node_info_defer)
        self.reactor.callLater(2.0, self._poll_ln_funds_defer)
        self.reactor.callLater(2.0, self._poll_ln_nodes_defer)
