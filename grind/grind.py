# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


from bitcoind import StaticBitcoind
from block_stats import BlockStats

BLOCK_HASH = "00000000000000000002e7f112da8a9fe7b18b2781ee73dfba65b9485aa71b89"

StaticBitcoind.URL = StaticBitcoind.gen_url()

if __name__ == "__main__":

    height = StaticBitcoind.getblockchaininfo()['blocks']

    for h in range(height-10, height):
        block_hash = StaticBitcoind.getblockhash(h)
        bs = BlockStats(block_hash)
        print("------ Block %d ---------" % h)
        print(bs.run())
