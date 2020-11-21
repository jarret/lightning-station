# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from bitcoind import Bitcoind

CHAIN_DEPTH = 10

class DeepGrind():
    def __init__(self, publish_func):
        self.publish_func = publish_func
        self.tip_height = None

        self.block_results = {}

    def get_blocks_with_results(self):
       return self.block_results.key()

    def prune_results(self, tip_height):
        to_prune = 

    def check_tip(self):
        chain_info = Bitcoind.getblockchaininfo()
        if not chain_info:
            return
        blockheight = chain_info['blocks']
