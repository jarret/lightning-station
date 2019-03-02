import os

from twisted.internet import threads
from bitcoinrpc import Bitcoind
from lightningd import LightningDaemon

INTERVAL = 10.0

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
                'mempool_max':      mempool_info['maxmempool'],
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

    def _getinfofunds(lightning_rpc):
        ld = LightningDaemon(lightning_rpc)
        return ld.getinfo(), ld.listfunds(), ld.listnodes()


    def _sum_funds(funds):
        def msat2int(msat_str):
            assert msat_str.endswith("msat")
            return int(msat_str[:-4])
        chain = sum(msat2int(o['amount_msat']) for o in funds['outputs'])
        total = sum(msat2int(c['amount_msat']) for c in funds['channels'])
        ours = sum(msat2int(c['our_amount_msat']) for c in funds['channels'])
        theirs = total - ours
        return theirs, ours, chain

    def _sum_nodes(nodes):
        return len(nodes['nodes'])

    def _poll_ln_node_info_thread_func(lightning_rpc):
        info, funds, nodes = LnNodeInfo._getinfofunds(lightning_rpc)
        theirs, ours, chain = LnNodeInfo._sum_funds(funds)
        n_nodes = LnNodeInfo._sum_nodes(nodes)
        return {'ln_version':           info['version'],
                'ln_inet_peers':        info['num_peers'],
                'ln_node_peers':        n_nodes,
                'ln_alias':             info['alias'],
                'ln_channels_pending':  info['num_pending_channels'],
                'ln_channels_active':   info['num_active_channels'],
                'ln_channels_inactive': info['num_inactive_channels'],
                'ln_channel_ours':      ours,
                'ln_channel_theirs':    theirs,
                'ln_channel_chain':     chain,
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
