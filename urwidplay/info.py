# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time

DEFAULT_INFO = {
    'tip_block_height': 0,
    'tip_block_size':   0,
    'tip_block_weight': 0,
    'tip_block_hash':   "",
    'time':             time.time(),
    'price_btccad':     17464.25,
    'total_supply':     18525896.48986026,
    'cpu_pcts':         [10, 20, 30, 40],
    'mem_total':        1024 * 1024 * 1024,
    'mem_used':         1024 * 1024 * 512,
    'mem_used_pct':     50,
    'block_height':     654444,
    'block_arrival_timestamp': 1603658136,
    'block_timestamp':         1603658133,
    'block_n_txes':     1234,
    'block_size':       1024 * 1024,
    'block_weight':     3 * 1024 * 1024,
}

class Info(dict):
    def __init__(self):
        super().__init__()
        self.update(DEFAULT_INFO)

    def update_info(self, title, new_info):
        self[title] = new_info
