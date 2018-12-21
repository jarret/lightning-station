#!/usr/bin/env python3

import urwid
import time

from twisted.internet import reactor, threads, task

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

from tawker import Tawker
from gen_name import gen_block_name
from bitcoinrpc import Bitcoind
from phrases import get_phrase
from ip_address import get_ip_address


###############################################################################

COLS = 130
ROWS = 40

def assert_terminal_size(current_cols, current_rows):
    s = "terminal size must be %dx%d, curently: %dx%d" % (
        COLS, ROWS, current_cols, current_rows)
    assert current_cols == COLS, s
    assert current_rows == ROWS, s

###############################################################################

NEW_BLOCK_QUEUE = {'running': False,
                   'queue':   [],
                  }

#STATES = {'INIT', 'GETTING_BLOCK_INFO', 'OUTPUTTING'}

class NewBlock(object):
    def __init__(self, block_hash):
        print("newblock class init")
        self.block_info = {'hash': block_hash}
        #self.state = "INIT"

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
        NewBlock.finish()

    def _speak_line_defer(self):
        print("speak defer")
        d = threads.deferToThread(NewBlock._speak_line_thread_func,
                                  self.block_info['height'],
                                  self.block_info['name'],
                                  self.block_info['phrase'])
        d.addCallback(self._speak_line_callback)

    ###########################################################################

    def _screen_output_lines(self):
        yield "=" * 77
        yield "name: %s" % self.block_info['name']
        yield "phrase: %s" % self.block_info['phrase']
        yield "size: %d bytes" % self.block_info['size']
        yield "weight: %d bytes" % self.block_info['weight']
        yield "n_transactions: %d" % len(self.block_info['tx'])
        yield "n tx: %d" % self.block_info['nTx']
        yield "raw block chars: %d" % len(self.block_info['raw'])
        yield "time: %d" % self.block_info['time']
        yield "mediantime: %d" % self.block_info['mediantime']
        yield "=" * 77

    def _screen_output(self):
        return '\n'.join(self._screen_output_lines())

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
        self.block_info.update(result)
        print(self._screen_output())
        self._speak_line_defer()

    def _getblock_cmd_defer(self):
        print("getblock defer")
        d = threads.deferToThread(NewBlock._getblock_cmd_thread_func,
                                  self.block_info['hash'])
        d.addCallback(self._getblock_cmd_callback)

    ###########################################################################

    def run(self):
        print("run")
        self._getblock_cmd_defer()

    ###########################################################################

    def finish():
        print("finish")
        NEW_BLOCK_QUEUE['running'] = False
        NewBlock.try_next()

    def try_next():
        print("try next")
        if ((NEW_BLOCK_QUEUE['running'] == False) and
            (len(NEW_BLOCK_QUEUE['queue']) > 0)):
            NEW_BLOCK_QUEUE['running'] = True
            new_block = NEW_BLOCK_QUEUE['queue'].pop()
            new_block.run()

    def listener(message):
        print("listener")
        new_block = NewBlock(message[1].hex())
        NEW_BLOCK_QUEUE['queue'].append(new_block)
        NewBlock.try_next()

###############################################################################


class StatUpdate(object):

    def _screen_output_lines(self, info):
        yield "=" * 77
        yield "mempool txs: %d" % info['mempool']['size']
        yield "mempool bytes: %d" % info['mempool']['usage']
        mempool_pct = ((info['mempool']['usage'] /
                        info['mempool']['maxmempool']) * 100.00)
        yield "local mem capacity: %.2f%%" % (mempool_pct)
        yield "=" * 77
        yield "LAN ip: %s" % info['ip_address']
        yield "version: %d" % info['network']['version']
        yield "net connections: %d" % info['network']['connections']
        yield "version: %s" % info['network']['subversion']
        yield "=" * 77
        estimate_1 = info['fee_estimate_1']['feerate'] * 100000.0
        yield "fee estimate 1 block:      %0.2f sat/byte" % estimate_1
        estimate_3 = info['fee_estimate_3']['feerate'] * 100000.0
        yield "fee estimate 3 blocks:     %0.2f sat/byte" % estimate_3
        estimate_6 = info['fee_estimate_6']['feerate'] * 100000.0
        yield "fee estimate 6 blocks:     %0.2f sat/byte" % estimate_6
        estimate_12 = info['fee_estimate_12']['feerate'] * 100000.0
        yield "fee estimate 12 blocks:    %0.2f sat/byte" % estimate_12
        estimate_24 = info['fee_estimate_24']['feerate'] * 100000.0
        yield "fee estimate 24 blocks:    %0.2f sat/byte" % estimate_24
        estimate_48 = info['fee_estimate_48']['feerate'] * 100000.0
        yield "fee estimate 48 blocks:    %0.2f sat/byte" % estimate_48
        estimate_100 = info['fee_estimate_100']['feerate'] * 100000.0
        yield "fee estimate 100 blocks:   %0.2f sat/byte" % estimate_100
        estimate_500 = info['fee_estimate_500']['feerate'] * 100000.0
        yield "fee estimate 500 blocks:   %0.2f sat/byte" % estimate_500
        yield "=" * 77

    def _screen_output(self, info):
        return '\n'.join(self._screen_output_lines(info))

    def run(self):
        info = {}
        info['ip_address'] = get_ip_address()
        info['mempool'] = Bitcoind.getmempoolinfo()
        info['network'] = Bitcoind.getnetworkinfo()
        info['fee_estimate_1'] = Bitcoind.estimatesmartfee(1)
        info['fee_estimate_3'] = Bitcoind.estimatesmartfee(3)
        info['fee_estimate_6'] = Bitcoind.estimatesmartfee(6)
        info['fee_estimate_12'] = Bitcoind.estimatesmartfee(12)
        info['fee_estimate_24'] = Bitcoind.estimatesmartfee(24)
        info['fee_estimate_48'] = Bitcoind.estimatesmartfee(48)
        info['fee_estimate_100'] = Bitcoind.estimatesmartfee(100)
        info['fee_estimate_500'] = Bitcoind.estimatesmartfee(500)
        print(self._screen_output(info))

###############################################################################

def setup_zmq_block_listener(block_func):
    s = ZmqSubConnection(ZmqFactory(),
                         ZmqEndpoint("connect", "tcp://127.0.0.1:28332"))
    s.subscribe("hashblock".encode("utf-8"))
    s.messageReceived = block_func

def node_stat_update():
    print("stat update")
    su = StatUpdate()
    su.run()

###############################################################################

PALETTE = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', 'g7', '#d06'),
    ('headings', 'white,underline', 'black', 'bold,underline'),
    ('body_text', 'dark cyan', 'light gray'),
          ]

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def setup_base_loop():
    background_widget = urwid.SolidFill()
    #print("sizing: %s" % placeholder.sizing())
    loop = urwid.MainLoop(background_widget, PALETTE,
                          event_loop=urwid.TwistedEventLoop(reactor=reactor),
                          unhandled_input=exit_on_q)
    cols, rows = loop.screen.get_cols_rows()
    assert_terminal_size(cols, rows)
    loop.screen.set_terminal_properties(colors=256)
    loop.widget = urwid.AttrMap(background_widget, 'bg')
    return loop

def setup_urwid_loop():
    loop = setup_base_loop()

    loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

    #div = urwid.Divider()
    #outside = urwid.AttrMap(div, 'outside')
    #inside = urwid.AttrMap(div, 'inside')
    txt = urwid.Text(('banner', u" Hello World "), align='center')
    streak = urwid.AttrMap(txt, 'headings')
    pile = loop.widget.base_widget # .base_widget skips the decorations
    pile.contents.append((streak, pile.options()))

    return loop



###############################################################################
LOOP = None

def update_time(start_time):
    elapsed = time.time() - start_time
    #print("update %d" % elapsed)
    #print("%s" % LOOP)
    txt = urwid.Text(('banner', u" %d elapsed " % elapsed), align='center')
    newstreak = urwid.AttrMap(txt, 'headings')
    pile = LOOP.widget.base_widget # .base_widget skips the decorations
    pile.contents.pop()
    pile.contents.append((newstreak, pile.options()))
    LOOP.draw_screen()


###############################################################################

if __name__ == '__main__':
    setup_zmq_block_listener(NewBlock.listener)

    l = task.LoopingCall(node_stat_update)
    l.start(3.0, now=False)

    LOOP = setup_urwid_loop()

    start_time = time.time()

    t = task.LoopingCall(update_time, start_time)
    t.start(1.0, now=False)

    LOOP.run()
