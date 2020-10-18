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
    'price_btccad':     12345.00,
    'total_supply':     18520229.72786026,
}

class Info(dict):
    def __init__(self):
        super().__init__()
        self.update(DEFAULT_INFO)

    def update_info(self, title, new_info):
        self[title] = new_info
