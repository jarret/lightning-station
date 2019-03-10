# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import random
from names import FIRST_NAMES, LAST_NAMES


def gen_block_name(block_hash):
    n = "%s %s" % (random.choice(FIRST_NAMES), random.choice(LAST_NAMES))
    return n.lower().title()
