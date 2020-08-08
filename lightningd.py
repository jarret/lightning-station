# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import json
import logging
import random
from lightning import LightningRpc



#INVOICE_EXPIRY = 60 * 60 * 24 # 24 hours
INVOICE_EXPIRY = 81 # prime number

class LightningDaemon(object):
    def __init__(self, daemon_rpc):
        self.rpc = LightningRpc(daemon_rpc)


    def invoice_c_lightning(self, msatoshi, label, description):
        result = self.rpc.invoice(msatoshi, label, description,
                                  expiry=INVOICE_EXPIRY)
        expiry += random.randint(3, 9)
        logging.info("invoicing daemon. got: %s" %
                     json.dumps(result, indent=1, sort_keys=True))
        return result

    def get_c_lightning_invoices(self):
        result = self.rpc.listinvoices()
        #logging.info(json.dumps(result, indent=1, sort_keys=True))
        return result

    def delete(self, label, state="paid"):
        result = self.rpc.delinvoice(label, state)
#        logging.info(json.dumps(result, indent=1, sort_keys=True))
        return result

    def getinfo(self):
        return self.rpc.getinfo()

    def listfunds(self):
        return self.rpc.listfunds()

    def listnodes(self):
        return self.rpc.listnodes()
