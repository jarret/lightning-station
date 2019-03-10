# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import logging
from eink_ui import EinkUI

logging.CONSOLE = True
eu = EinkUI()

#print(eu.gen_qrcode_bytes().hex())
print(eu.gen_screen_bytes())
