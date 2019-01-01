import urwid
import datetime
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
        #self._assert_terminal_size(cols, rows)
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

    def _fmt_timestamp(self, timestamp):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        return str(dt)

    def _fmt_seconds(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return "%d minutes %d seconds" % (m, s)

    ###########################################################################

    def _wrap_box(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'background')

    def _wrap_filler(self, widget):
        f = urwid.Filler(widget)
        return urwid.AttrMap(f, 'background')

    ###########################################################################

    def _fee_estimate_widget(self):
        if 'fee_estimate' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no fee estimates)")
        lines = []
        for block in sorted(self.info['fee_estimate'].keys()):
            estimate = self.info['fee_estimate'][block]
            s = "%d: %0.2f sat/byte" % (block, estimate)
            lines.append(self._center_info_text(s))
        return self._wrap_box(urwid.Pile(lines), "Conservative Fee Estimates")

    def _fee_estimate_eco_widget(self):
        if 'fee_estimate_eco' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no eco fee estimates)")
        lines = []
        for block in sorted(self.info['fee_estimate_eco'].keys()):
            estimate = self.info['fee_estimate_eco'][block]
            s = "%d: %0.2f sat/byte" % (block, estimate)
            lines.append(self._center_info_text(s))
        return self._wrap_box(urwid.Pile(lines), "Econmical Fee Estimates")

    def _mempool_widget(self):
        if 'mempool_txs' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no mempool data)")

        t = self._center_info_text("txs: {:,}".format(self.info['mempool_txs']))
        b = self._center_info_text("bytes: {:,}".format(
            self.info['mempool_bytes']))
        p = self._progress_bar('used', 'free', self.info['mempool_percent'])
        lines = [t, b, p]
        return self._wrap_box(urwid.Pile(lines), "Mempool")

    def _network_widget(self):
        if 'net_connections' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no network data)")
        c = self._center_info_text("connections: %d" %
                                   self.info['net_connections'])
        v = self._center_info_text("version: %s" %
                                   self.info['net_version'])
        lines = [c, v]
        if 'ip_address' in self.info:
            i = self._center_info_text("LAN IP: %s" % self.info['ip_address'])
            lines.append(i)
        return self._wrap_box(urwid.Pile(lines), "Network")


    def _block_widget(self):
        if 'block_name' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no block data)")
        h = self._center_info_text("height: %d" %
                                    self.info['block_height'])
        bn = self._center_info_text("name: %s" %
                                     self.info['block_name'])
        p = self._center_info_text(self.info['block_phrase'])
        arrival = self.info['block_arrival_time']
        at = self._center_info_text(
            "arrival: %s" % self._fmt_timestamp(arrival))
        tx = self._center_info_text(
            "txs: {:,}".format(self.info['block_n_txes']))

        s = self._center_info_text(
            "size: {:,} bytes".format(self.info['block_size']))
        w = self._center_info_text(
            "weight: {:,} bytes".format(self.info['block_weight']))
        t = self._center_info_text(
            "timestamp: %s" % self._fmt_timestamp(self.info['block_timestamp']))
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._center_info_text("elapsed: %s" % self._fmt_seconds(elapsed))

        lines = [h, bn, p, at, tx, s, w, t, e]
        return self._wrap_box(urwid.Pile(lines), "Block")

    def _websocket_widget(self):
        if 'ws_tally' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no websocket data)")
        t = self._center_info_text("tally: %d" % self.info['ws_tally'])
        lines = [t]
        return self._wrap_box(urwid.Pile(lines), "Websocket")

    def _sys_res_widget(self):
        if 'mem_total' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no sys res data)")
        t = self._center_info_text(
            "Mem Total: {:,} bytes".format(self.info['mem_total']))
        p = self._progress_bar('used', 'free', self.info['mem_used_pct'])
        s = self._center_info_text(
            "Net Send: {:,} bytes/s".format(self.info['net_send']))
        r = self._center_info_text(
            "Net Recv: {:,} bytes/s".format(self.info['net_recv']))
        rd = self._center_info_text(
            "Disk Read: {:,} bytes/s".format(self.info['disk_read']))
        wt = self._center_info_text(
            "Disk write: {:,} bytes/s".format(self.info['disk_write']))
        d = self._center_info_text(
            "Blockchain Dir: {:,} bytes".format(self.info['dir_size']))
        c = self._center_info_text("CPU Usage:")
        lines = [t, p, s, r, rd, wt, d, c]
        for cpu in self.info['cpu_pct']:
            lines.append(self._progress_bar('used', 'free', cpu))
        return self._wrap_box(urwid.Pile(lines), "System Resources")

    def _song_playing_widget(self):
        if 'song_playing_title' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no song playing)")
        if not self.info['song_playing_title']:
            return self._wrap_box(urwid.Pile([]), "(no song playing)")
        st = self._center_info_text(
            "Title: %s" % self.info['song_playing_title'])
        sa = self._center_info_text(
            "Artist: %s" % self.info['song_playing_artist'])
        lines = [st, sa]
        return self._wrap_box(urwid.Pile(lines), "Now Playing")

    def _song_queue_widget(self):
        if 'queued_songs' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no songs queued)")
        n = len(self.info['queued_songs'])
        if n == 0:
            return self._wrap_box(urwid.Pile([]), "(no songs queued)")

        showing = min(n, 5)
        not_showing = (n - 5) if (n > 5) else 0

        lines = []
        songs = self.info['queued_songs']
        for i in range(showing):
            song = songs[i]
            t = self._center_info_text("%d) Title: %s" % (i, song['title']))
            lines.append(t)
            a = self._center_info_text("   Artist: %s" % song['artist'])
            lines.append(a)
        if not_showing != 0:
            m = self._center_info_text("(%d more)" % not_showing)
            lines.append(m)
        return self._wrap_box(urwid.Pile(lines), "Song Queue")

    ###########################################################################

    def _build_widgets(self):
        fee = self._fee_estimate_widget()
        eco = self._fee_estimate_eco_widget()
        mem = self._mempool_widget()
        net = self._network_widget()
        blk = self._block_widget()
        sr = self._sys_res_widget()
        ws = self._websocket_widget()
        sp = self._song_playing_widget()
        sq = self._song_queue_widget()

        col1 = self._wrap_filler(urwid.Pile([fee, eco, mem]))
        col2 = self._wrap_filler(urwid.Pile([net, blk, sr]))
        col3 = self._wrap_filler(urwid.Pile([ws, sp, sq]))
        cols = urwid.Columns([col1, col2, col3])

        self.loop.widget = cols

    ###########################################################################

    def update_info(self, new_info):
        self.info.update(new_info)
        #log(json.dumps(new_info, indent=1, sort_keys=True))
        if self.console:
            #log(json.dumps(new_info, indent=1, sort_keys=True))
            return

        self._build_widgets()
        self.loop.draw_screen()

    ###########################################################################

    def start_event_loop(self):
        self.loop.run()

    def stop(self):
        urwid.ExitMainLoop()
