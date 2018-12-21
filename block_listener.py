from twisted.internet import threads
from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection

from bitcoinrpc import Bitcoind
from gen_name import gen_block_name
from phrases import get_phrase
from tawker import Tawker

################################################################################

class NewBlock(object):
    def __init__(self, new_block_queue, block_hash, screen_ui):
        self.new_block_queue = new_block_queue
        self.block_hash = block_hash
        self.screen_ui = screen_ui
        self.arrival_time = time.time()

    ###########################################################################

    def _speak_line_thread_func(height, name, phrase):
        print("speak thread func")
        tawker = Tawker()
        line = 'New block: %d. I dub thee "%s."' % (height, name)
        tawker.tawk(line)
        time.sleep(0.3)
        tawker.tawk(phrase)
        return line + " " + phrase

    def _speak_line_callback(self, result):
        print("spoke line: %s" % result)
        self.new_block_queue.finish_block()

    def _speak_line_defer(self, info):
        print("speak defer")
        d = threads.deferToThread(NewBlock._speak_line_thread_func,
                                  info['block_height'],
                                  info['name'],
                                  info['block_phrase'])
        d.addCallback(self._speak_line_callback)

    ###########################################################################

    def _getblock_cmd_thread_func(block_hash):
        print("getblock thread func")
        info = Bitcoind.getblock(block_hash)
        raw = Bitcoind.getblock_raw(block_hash)
        info['raw'] = raw
        info['name'] = gen_block_name(block_hash)
        info['phrase'] = get_phrase()
        return info

    def _getblock_cmd_callback(self, result):
        print("getblock callback")
        info = {'block_arrival_time': self.arrival_time,
                'block_name':         result['name'],
                'block_phrase':       result['phrase'],
                'block_height':       result['height'],
                'block_n_txes':       result['nTx'],
                'block_size':         result['size'],
                'block_weight':       result['weight'],
                'block_timestamp':    result['time'],
               }
        self._speak_line_defer(info)
        self.screen_ui.update_info(info)

    def _getblock_cmd_defer(self):
        print("getblock defer")
        d = threads.deferToThread(NewBlock._getblock_cmd_thread_func,
                                  self.block_hash)
        d.addCallback(self._getblock_cmd_callback)

    ###########################################################################

    def run(self):
        print("run")
        self._getblock_cmd_defer()

################################################################################

class NewBlockQueue(object):
    """ New blocks that arrive are notified to us from bitcoind via ZeroMQ.
        They are queued up for handling since they can arrive faster than
        they are able to be handled.
    """
    def __init__(self, reactor, screen_ui):
        f = ZmqFactory()
        f.reactor = reactor
        e = ZmqEndpoint("connect", "tcp://127.0.0.1:28332")
        s = ZmqSubConnection(f, e)
        s.subscribe("hashblock".encode("utf-8"))
        s.messageReceived = self.listener
        self.screen_ui = screen_ui
        self.new_block_queue = []
        self.queue_running = False

    def finish_block(self):
        print("finish")
        self.queue_running = False
        self._try_next()

    def _try_next(self):
        if (self.queue_running == False) and (len(self.new_block_queue) > 0):
            self.queue_running = True
            new_block = self.new_block_queue.pop()
            new_block.run()

    def listener(self):
        new_block = NewBlock(self, message[1].hex(), self.screen_ui)
        self.new_block_queue.append(new_block)
        self._try_next()
