# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import krakenex

class KrakenPrice():
    def fetch_btccad():
        try:
            k = krakenex.API()
            ticker = k.query_public('Ticker', {'pair': 'XXBTZCAD'})
            last_close_raw = ticker["result"]["XXBTZCAD"]["c"]
            last_close = last_close_raw[0]
            return float(last_close)
        except:
            return None

    def fetch_btcusd():
        try:
            k = krakenex.API()
            ticker = k.query_public('Ticker', {'pair': 'XXBTZUSD'})
            last_close_raw = ticker["result"]["XXBTZUSD"]["c"]
            last_close = last_close_raw[0]
            return float(last_close)
        except:
            return None

    def fetch_btceur():
        try:
            k = krakenex.API()
            ticker = k.query_public('Ticker', {'pair': 'XXBTZEUR'})
            last_close_raw = ticker["result"]["XXBTZEUR"]["c"]
            last_close = last_close_raw[0]
            return float(last_close)
        except:
            return None

    def fetch_btcgbp():
        try:
            k = krakenex.API()
            ticker = k.query_public('Ticker', {'pair': 'XXBTZGBP'})
            last_close_raw = ticker["result"]["XXBTZGBP"]["c"]
            last_close = last_close_raw[0]
            return float(last_close)
        except:
            return None
