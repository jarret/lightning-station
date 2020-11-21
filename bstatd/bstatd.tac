# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys
import os

from twisted.application import service

path = os.path.dirname(os.path.realpath(__file__))
print(path)
sys.path.insert(0, path)
from bstatd import Bstatd

application = service.Application("Bitcoind Stat Daemon")
service = Bstatd()
service.setServiceParent(application)
