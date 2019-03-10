# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import json
from lightning import LightningRpc

from logger import log


INVOICE_EXPIRY = 60 * 60 * 24 # 24 hours

class LightningDaemon(object):
    def __init__(self, daemon_rpc):
        self.rpc = LightningRpc(daemon_rpc)


    def invoice_c_lightning(self, msatoshi, label, description):
        result = self.rpc.invoice(msatoshi, label, description,
                                  expiry=INVOICE_EXPIRY)
        log(json.dumps(result, indent=1, sort_keys=True))
        return result

    def get_c_lightning_invoices(self):
        result = self.rpc.listinvoices()
        #log(json.dumps(result, indent=1, sort_keys=True))
        return result

    def delete(self, label, state="paid"):
        result = self.rpc.delinvoice(label, state)
#        log(json.dumps(result, indent=1, sort_keys=True))
        return result

    def getinfo(self):
        return self.rpc.getinfo()

    def listfunds(self):
        return self.rpc.listfunds()

    def listnodes(self):
        return self.rpc.listnodes()
