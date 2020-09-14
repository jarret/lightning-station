#!/usr/bin/env python3
# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import time
import sys
from bitcoind import StaticBitcoind
from block_stats import BlockStats

BLOCK_HASH = "00000000000000000002e7f112da8a9fe7b18b2781ee73dfba65b9485aa71b89"

StaticBitcoind.URL = StaticBitcoind.gen_url()

if __name__ == "__main__":

    try:
        start_block = int(sys.argv[1])
        end_block = int(sys.argv[2])
    except:
        sys.exit("please provide start_block and end_block integers")

    height = StaticBitcoind.getblockchaininfo()['blocks']

    if start_block > height:
        sys.exit("start block too large")
    if end_block > height:
        sys.exit("end block too large")

    for h in range(height-10, height):
        start_time = time.time()
        block_hash = StaticBitcoind.getblockhash(h)
        bs = BlockStats(block_hash)
        print("------ Block %d ---------" % h)
        print(bs.run())
        print("elapsed for block %d: %0.3f seconds" % (
            h, time.time() - start_time))
