# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import subprocess
from gen_name import gen_block_name

TAWK_CMD = "espeak -v en-us"

class Tawker(object):
    def tawk(self, line):
        p = subprocess.Popen(TAWK_CMD.split(" "), stdin=subprocess.PIPE,
                             stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
        p.stdin.write(line.encode('utf-8'))
        p.stdin.close()
        p.wait()

if __name__ == '__main__':
    t = Tawker()
    name = gen_block_name("asdfasdf")
    t.tawk('new block 553627. I dub thee "%s."' % name)
