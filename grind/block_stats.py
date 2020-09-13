# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from bitcoind import Bitcoind
from bitcoind import StaticBitcoind

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
        info = StaticBitcoind.gettx_json(txid)
        value = info['vout'][vout]['value']
        otype = info['vout'][vout]['scriptPubKey']['type']
        return (value, otype)

    def gather_txindex_proc(self):
        print("proc gathering...")
        refs = list(self.iter_input_refs())
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            for ref, info in zip(refs,
                                 e.map(BlockStats.get_input_info, refs)):
                #print("%s %s" % (ref, info))
                self.txindex[self.ref_str(ref[0], ref[1])] = info

        #print("index: %s" % json.dumps(self.txindex))
        print("indexed: %s" % len(self.txindex))

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

    def commas(self, val):
        return '{val:,}'.format(val=val)

    def crunch_str(self, vals):
        return ("min: %16.8f  max: %16.8f  mean: %16.8f  "
                "median: %16.8f" % (min(vals), max(vals),
                                    statistics.mean(vals),
                                    statistics.median(vals)))

    def iter_stat_lines(self):
        info = self.block_info
        sizes = [tx['size'] for tx in info['tx']]
        vsizes = [tx['vsize'] for tx in info['tx']]
        nvins = [len(tx['vin']) for tx in info['tx']]
        nvouts = [len(tx['vout']) for tx in info['tx']]
        values = [sum(self.get_output_value(o) for o in tx['vout'])
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
        rpo = [o for o in outputs if self.get_output_type(o)]

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
        new_coins = sum(values) - sum(input_values)

        coinbase_tx = info['tx'][0]
        assert 'coinbase' in coinbase_tx['vin'][0]
        coinbase_out = coinbase_tx['vout'][0]['value']
        fees_collected = coinbase_out - new_coins

        yield "height: %d" % info['height']
        yield "block_hash: %s" % self.block_hash
        yield "size:           %s" % self.commas(info['size'])
        yield "weight:         %s" % self.commas(info['weight'])
        yield "---"
        yield "n transactions: %d" % len(info['tx'])
        yield "n inputs:       %d" % len(inputs)
        yield "n outputs       %d" % len(outputs)
        yield "utxo set delta: %d" % utxo_delta
        yield "---"
        yield "total input BTC:              %0.8f" % sum(input_values)
        yield "total output BTC:             %0.8f" % sum(values)
        yield "new coins BTC:                %0.8f" % new_coins
        yield "miner fees BTC:               %0.8f" % fees_collected
        yield "---"
        yield "n 1-prefixed inputs:          %d" % len(opi)
        yield "n 3-prefixed inputs:          %d" % len(tpi)
        yield "n key bc1-prefixed inputs:    %d" % len(bpi)
        yield "n script bc1-prefixed inputs: %d" % len(spi)
        yield "---"
        yield "n 1-prefixed outputs:          %d" % len(opo)
        yield "n 3-prefixed outputs:          %d" % len(tpo)
        yield "n key bc1-prefixed outputs:    %d" % len(bpo)
        yield "n script bc1-prefixed outputs: %d" % len(spo)
        yield "n OP_RETURN outputs:           %d" % len(rpo)
        yield "---"
        yield "tx size -      %s" % self.crunch_str(sizes)
        yield "tx vsize -     %s" % self.crunch_str(vsizes)
        yield "tx num vins -  %s" % self.crunch_str(nvins)
        yield "tx num vouts - %s" % self.crunch_str(nvouts)
        yield "tx out BTC -   %s" % self.crunch_str(values)


    def stat_str(self):
        return "\n".join(self.iter_stat_lines())

    ###########################################################################

    def run(self):
        self.block_info = self.bitcoind.getblock_json(self.block_hash)
        #self.gather_txindex_thread()
        self.gather_txindex_proc()
        return self.stat_str()

#BLOCK_HASH = "00000000000000000002e7f112da8a9fe7b18b2781ee73dfba65b9485aa71b89"
#
#StaticBitcoind.URL = StaticBitcoind.gen_url()
#
#if __name__ == "__main__":
#    bs = BlockStats(BLOCK_HASH)
#
#    bs.run()
