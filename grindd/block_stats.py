# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from bitcoind import Bitcoind

import time
import json
import statistics

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor


class BlockStats():
    def __init__(self, block_hash, max_workers=4):
        self.block_hash = block_hash
        self.bitcoind = Bitcoind()
        self.block_info = None
        self.txindex = {}
        self.max_workers = max_workers
        self.starttime = None

    ###########################################################################

    def iter_input_txids(self):
        #print(json.dumps(self.block_info, indent=1))
        for tx in self.block_info['tx']:
            for vin in tx['vin']:
                if 'coinbase' in vin:
                    continue
                yield vin['txid']

    def index_txid(self, txid):
        info = self.bitcoind.gettx_json(txid)
        value = info['vout'][vout]['value']
        otype = info['vout'][vout]['scriptPubKey']['type']
        self.txindex[txid] = (value, otype)

    def gather_txindex_thread(self):
        print("thread gathering...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            for txid in self.iter_input_txids():
                e.submit(self.index_txid, txid)
        print("indexed: %s" % len(self.txindex))

    ###########################################################################

    def ref_str(self, txid, vout):
        return "%s:%d" % (txid, vout)

    def iter_input_refs(self):
        #print(json.dumps(self.block_info, indent=1))
        for tx in self.block_info['tx']:
            for vin in tx['vin']:
                if 'coinbase' in vin:
                    continue
                yield vin['txid'], vin['vout']

    def get_input_info(ref):
        txid = ref[0]
        vout = ref[1]
        info = Bitcoind.gettx_json(txid)
        value = info['vout'][vout]['value']
        otype = info['vout'][vout]['scriptPubKey']['type']
        return (value, otype)

    def gather_txindex_proc(self):
        print("proc gathering...")
        self.starttime = time.time()
        refs = list(self.iter_input_refs())
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            for ref, info in zip(refs,
                                 e.map(BlockStats.get_input_info, refs)):
                #print("%s %s" % (ref, info))
                self.txindex[self.ref_str(ref[0], ref[1])] = info

        print("block crunch time: %0.4f" % (time.time() - self.starttime))

    ###########################################################################

    def get_input_type(self, iput):
        txid = iput['txid']
        vout = iput['vout']
        return self.txindex[self.ref_str(txid, vout)][1]

    def get_input_value(self, iput):
        txid = iput['txid']
        vout = iput['vout']
        return self.txindex[self.ref_str(txid, vout)][0]

    def get_output_type(self, oput):
        return oput['scriptPubKey']['type']

    def get_output_value(self, oput):
        return oput['value']

    ###########################################################################

    def crunch_vals(self, vals):
        return {"min":    min(vals),
                "max":    max(vals),
                "mean":   statistics.mean(vals),
                "median": statistics.median(vals)}

    def stat_dict(self):
        info = self.block_info
        sizes = [tx['size'] for tx in info['tx']]
        vsizes = [tx['vsize'] for tx in info['tx']]
        nvins = [len(tx['vin']) for tx in info['tx']]
        nvouts = [len(tx['vout']) for tx in info['tx']]
        output_values = [sum(self.get_output_value(o) for o in tx['vout'])
                  for tx in info['tx']]
        outputs = []
        for tx in info['tx']:
            for o in tx['vout']:
                outputs.append(o)

        opo = [o for o in outputs if self.get_output_type(o) == 'pubkeyhash']
        tpo = [o for o in outputs if self.get_output_type(o) == 'scripthash']
        bpo = [o for o in outputs if
               self.get_output_type(o) == 'witness_v0_keyhash']
        spo = [o for o in outputs if
               self.get_output_type(o) == 'witness_v0_scripthash']
        rpo = [o for o in outputs if self.get_output_type(o) == "nulldata"]
        #for o in outputs:
        #    print(self.get_output_type(o))

        inputs = []
        for tx in info['tx']:
            for i in tx['vin']:
                if 'coinbase' in i:
                    continue
                inputs.append(i)

        utxo_delta = len(outputs) - len(inputs)

        opi = [i for i in inputs if
               self.get_input_type(i) == 'pubkeyhash']
        tpi = [i for i in inputs if
               self.get_input_type(i) == 'scripthash']
        bpi = [i for i in inputs if
               self.get_input_type(i) == 'witness_v0_keyhash']
        spi = [i for i in inputs if
               self.get_input_type(i) == 'witness_v0_scripthash']

        input_values = [self.get_input_value(i) for i in inputs]
        new_coins = round(sum(output_values) - sum(input_values), 8)

        coinbase_tx = info['tx'][0]
        assert 'coinbase' in coinbase_tx['vin'][0]
        coinbase_out = coinbase_tx['vout'][0]['value']
        fees_collected = round(coinbase_out - new_coins, 8)

        r = {}
        r['height'] = info['height']
        r['block_hash'] = self.block_hash
        r['size'] = info['size']
        r['weight'] = info['weight']
        r['n_transactions'] = len(info['tx'])
        r['n_inputs'] = len(inputs)
        r['n_outputs'] = len(outputs)
        r['utxo_delta'] = utxo_delta
        r['total_input_btc'] = round(sum(input_values), 8)
        r['total_output_btc'] = round(sum(output_values), 8)
        r['new_coins'] = new_coins
        r['miner_fees'] = fees_collected
        r['1_prefixed_inputs'] = len(opi)
        r['3_prefixed_inputs'] = len(tpi)
        r['key_bc1_prefixed_inputs'] = len(bpi)
        r['script_bc1_prefixed_inputs'] = len(spi)
        r['1_prefixed_outputs'] = len(opo)
        r['3_prefixed_outputs'] = len(tpo)
        r['key_bc1_prefixed_outputs'] = len(bpo)
        r['script_bc1_prefixed_outputs'] = len(spo)
        r['op_return_outputs'] = len(rpo)
        r['tx_size'] = self.crunch_vals(sizes)
        r['tx_vsize'] = self.crunch_vals(vsizes)
        r['tx_n_vins'] = self.crunch_vals(nvins)
        r['tx_n_vouts'] = self.crunch_vals(nvouts)
        r['tx_out_btc'] = self.crunch_vals(output_values)
        return r

    ###########################################################################

    def run(self):
        self.block_info = self.bitcoind.getblock_json(self.block_hash)
        #self.gather_txindex_thread()
        self.gather_txindex_proc()
        return self.stat_dict()
