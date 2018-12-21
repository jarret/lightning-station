import urwid
import json
import time
from logger import log


COLS = 130
ROWS = 40

PALETTE = [('info_text', 'black', 'light gray'),
           ('background', '', '', '', 'g7', '#f60'),
           ('title_text', 'white,underline', 'black', 'bold,underline'),
          ]


class ScreenUI(object):
    def __init__(self, reactor, console):
        self.loop = self._setup_loop_background(reactor)
        self.info = self._init_info()
        self._build_widgets()
        self.console = console

    ###########################################################################

    def _init_info(self):
        return {'last_block': time.time()
               }

    ###########################################################################

    def _center_info_text(self, string):
        return urwid.Text(('info_text', " %s " % string), align='center')

    def _center_title_text(self, string):
        return urwid.Text(('title_text', string), align='center')

    def _progress_bar(self, normal, complete, pct):
        return urwid.ProgressBar(normal, complete, current=pct, done=100)

    ###########################################################################

    def _setup_loop_background(self, reactor):
        fill_widget = urwid.SolidFill()
        mapped_widget = urwid.AttrMap(fill_widget, 'background')
        event_loop = urwid.TwistedEventLoop(reactor=reactor)
        loop = urwid.MainLoop(mapped_widget, PALETTE,
                              event_loop=event_loop,
                              unhandled_input=self.exit_on_q)
        cols, rows = loop.screen.get_cols_rows()
        self._assert_terminal_size(cols, rows)
        loop.screen.set_terminal_properties(colors=256)
        return loop

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def _assert_terminal_size(self, cols, rows):
        s = "terminal size must be %dx%d, currently: %dx%d" % (
            COLS, ROWS, cols, rows)
        assert cols == COLS, s
        assert rows == ROWS, s

    ###########################################################################

    def _wrap_filler(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(f, 'background')

    def _fee_estimate_widget(self):
        if 'fee_estimate' not in self.info:
            return self._wrap_filler(urwid.Pile([]), "(no fee estimates)")
        lines = []
        for block in sorted(self.info['fee_estimate'].keys()):
            estimate = self.info['fee_estimate'][block]
            s = "%d: %0.2f sat/byte" % (block, estimate)
            lines.append(self._center_info_text(s))
        return self._wrap_filler(urwid.Pile(lines), "Fee Estimates")

    def _mempool_widget(self):
        if 'mempool_txs' not in self.info:
            return self._wrap_filler(urwid.Pile([]), "(no mempool data)")

        t = self._center_info_text("txs: {:,}".format(self.info['mempool_txs']))
        b = self._center_info_text("bytes: {:,}".format(
            self.info['mempool_bytes']))
        p = self._progress_bar('used', 'free', self.info['mempool_percent'])
        lines = [t, b, p]
        return self._wrap_filler(urwid.Pile(lines), "Mempool")

    def _network_widget(self):
        if 'net_connections' not in self.info:
            return self._wrap_filler(urwid.Pile([]), "(no network data)")
        c = self._center_info_text("connections: %d" %
                                   self.info['net_connections'])
        v = self._center_info_text("version: %s" %
                                   self.info['net_version'])
        lines = [c, v]
        if 'ip_address' in self.info:
            i = self._center_info_text("LAN IP: %s" % self.info['ip_address'])
            lines.append(i)
        return self._wrap_filler(urwid.Pile(lines), "Network")


    def _block_widget(self):
        if 'block_name' not in self.info:
            return self._wrap_filler(urwid.Pile([]), "(no block data)")
        h = self._center_info_text("height: %d" %
                                    self.info['block_height'])
        bn = self._center_info_text("name: %s" %
                                     self.info['block_name'])
        p = self._center_info_text(self.info['block_phrase'])
        at = self._center_info_text("arrival: %d" %
                                     self.info['block_arrival_time'])
        tx = self._center_info_text(
            "txs: {:,}".format(self.info['block_n_txes']))

        s = self._center_info_text(
            "size: {:,} bytes".format(self.info['block_size']))
        w = self._center_info_text(
            "weight: {:,} bytes".format(self.info['block_weight']))
        t = self._center_info_text(
            "timestamp: %d" % self.info['block_timestamp'])
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._center_info_text("elapsed: %d" % elapsed)

        lines = [h, bn, p, at, tx, s, w, t, e]
        return self._wrap_filler(urwid.Pile(lines), "Block")

    ###########################################################################

    def _build_widgets(self):
        fee = self._fee_estimate_widget()
        mem = self._mempool_widget()
        net = self._network_widget()
        blk = self._block_widget()

        col1 = urwid.Pile([fee, mem])
        col2 = urwid.Pile([net, blk])
        col3 = urwid.AttrMap(urwid.SolidFill(), "background")
        cols = urwid.Columns([col1, col2, col3])

        self.loop.widget = cols

    ###########################################################################

    def update_info(self, new_info):
        self.info.update(new_info)
        log(json.dumps(new_info, indent=1, sort_keys=True))
        if self.console:
            log(json.dumps(new_info, indent=1, sort_keys=True))
            return

        self._build_widgets()
        self.loop.draw_screen()

    ###########################################################################

    def start_event_loop(self):
        self.loop.run()

    def stop(self):
        self.loop.stop()
