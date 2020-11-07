# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import time
import json
import logging

DEFAULT_INFO = {
    'time':             time.time(),
    'price_btccad':     18000.0,
    'price_cadbtc':     1.0 / 18000.0,
    'total_supply':     18525896.48986026,
    'mkt_cap_cad':      300000000000,
    'cpu_pct':          [10, 20, 30, 40],
    'mem_total':        1024 * 1024 * 1024,
    'mem_used':         1024 * 1024 * 512,
    'mem_used_pct':     50,
    'block_height':     654444,
    'block_timestamp':         1603658133,
    'block_n_txes':     1234,
    'block_size':       1024 * 1024,
    'block_weight':     3 * 1024 * 1024,
    'blockchain_sizeondisk': 349255372928,
    'blockchain_height':     654946,
    'blockchain_difficulty': 19997335994446.11,
    'blockchain_tip_hash': "0000000000000000000d7255f918bfc0becd4d7fd795eb0f12549ca02658cfb2",
    'mempool_txes':     0,
    'mempool_mem_used': 0,
    'mempool_mem_max':  300000000,
    'mempool_bytes':    0,
    'network_version':  "/Satoshi:0.20.1/",
    'network_connections':  10,
    'fee_estimates':   {1:   10,
                        5:   9,
                        25:  8,
                        50:  7,
                        100: 6,
                        250: 5,
                        500: 4},
    'fee_estimates_eco': {1:   10,
                          5:   9,
                          25:  8,
                          50:  7,
                          100: 6,
                          250: 5,
                          500: 4},
    'last_block_arrive_time': 1603658136,
    'tip_ntx': 100,
    'tip_block_time': 1603658133,
    'tip_inputs': 100,
    'tip_outputs': 100,
    'tip_block_weight': 100,
    'tip_block_size': 100,
}

class Info(dict):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.filename = config['Panel']['PersistFile']
        logging.info("using: %s" % self.filename)
        self.make_exist(self.filename)
        persist_db = self.read_json(self.filename)
        self.update(persist_db)
        self.recalculate()

    ###########################################################################

    def make_exist(self, filename):
        if os.path.exists(filename):
            return
        logging.info("initializing new connect persist db: %s" % filename)
        dir_path = os.path.dirname(filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        record = DEFAULT_INFO.copy()
        self.write_json(filename, record)

    def write_file(self, path, content):
        f = open(path, 'w')
        f.write(content)
        f.close()

    def write_json(self, path, info, quick=True):
        content = (json.dumps(info) if quick else
                   json.dumps(info, indent=1, sort_keys=True))
        self.write_file(path, content)

    def read_json(self, path):
        f = open(path, 'r')
        c = f.read()
        info = json.loads(c)
        f.close()
        return info

    def persist(self):
        self.write_json(self.filename, self)

    def depersist(self):
        os.remove(self.filename)

    ###########################################################################

    def update_info(self, key, info):
        self[key] = info
        self.recalculate()
        self.persist()

    def recalculate(self):
        self['time'] = time.time()
        self['price_cadbtc'] = 1.0 / self['price_btccad']
        self['mkt_cap_cad'] = self['total_supply'] * self['price_btccad']
        logging.info("recalced")

