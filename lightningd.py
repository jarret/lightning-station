# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import json
import logging
import random
from pyln.client import LightningRpc



#INVOICE_EXPIRY = 60 * 60 * 24 # 24 hours
INVOICE_EXPIRY = 60 * 30

class LightningDaemon(object):
    def __init__(self, daemon_rpc):
        self.rpc = LightningRpc(daemon_rpc)

    def invoice_c_lightning(self, msatoshi, label, description):
        expiry = INVOICE_EXPIRY + random.randint(3, 9)
        try:
            result = self.rpc.invoice(msatoshi, label, description,
                                      expiry=expiry)
            logging.info("invoicing daemon. got: %s" %
                         json.dumps(result, indent=1, sort_keys=True))
            return result
        except:
            return None

    def get_c_lightning_invoices(self):
        try:
            return self.rpc.listinvoices()
        except:
            return None
        #logging.info(json.dumps(result, indent=1, sort_keys=True))

    def _delete(self, label, state="paid"):
        try:
            result = self.rpc.delinvoice(label, state)
            return result
        except IOError:
            # unpaid could have expired in the last split second due
            # to a race, so try again
            if state == "unpaid":
                result = self.rpc.delinvoice(label, "expired")
        return result

    def delete(self, label, state="paid"):
        try:
            return self._delete(label, state=state)
        except:
            return None

    def getinfo(self):
        try:
            return self.rpc.getinfo()
        except:
            return None

    def listfunds(self):
        try:
            return self.rpc.listfunds()
        except:
            return None

    def listnodes(self):
        try:
            return self.rpc.listnodes()
        except:
            return None
