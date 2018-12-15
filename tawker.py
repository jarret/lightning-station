import subprocess
from gen_name import gen_name

TAWK_CMD = "espeak -v en-us"

class Tawker(object):
    def tawk(self, line):
        p = subprocess.Popen(TAWK_CMD.split(" "), stdin=subprocess.PIPE)
        p.stdin.write(line.encode('utf-8'))
        p.stdin.close()

if __name__ == '__main__':
    t = Tawker()
    name = gen_name()
    t.tawk('new block 553627. I dub thee "%s."' % name)
