import urwid
import datetime
import json
import time
from logger import log

BACK = "#f60"
PANEL = "#fa0"
PANEL_ALT = "#f8d"
PANEL_ALT_2 = "#0ad"
PANEL_ALT_3 = "#f00"
PANEL_ALT_4 = "#0a0"

PALETTE = [
           #('info_text', 'black', 'light gray'),
           ('info_text', '', '', '', '#fff,bold', 'g7'),
           ('background', '', '', '', 'g7,bold', "g7"),
           ('panel_box', '', '', '', 'g7,bold', PANEL),
           ('panel_box_alt', '', '', '', 'g11,bold', PANEL_ALT),
           ('panel_box_alt_2', '', '', '', 'g11,bold', PANEL_ALT_2),
           ('panel_box_alt_3', '', '', '', 'g11,bold', PANEL_ALT_3),
           ('panel_box_alt_4', '', '', '', 'g11,bold', PANEL_ALT_4),
           ('title_text', 'white,underline', 'black', 'bold,underline'),
           ('unit_text', '', '', '', '#fff', 'g7'),
           ('label_text', '', '', '', 'g78', 'g7'),
           ('pb_normal', '', '', '', 'g19', BACK),
           ('pb_complete',  '', '', '', BACK, 'g19'),
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

    def _center_info_text_2(self, string):
        return urwid.Text(('info_text', "%s" % string), align='center')

    def _right_info_text(self, string):
        return urwid.Text(('info_text', "%s" % string), align='right')

    def _left_info_text(self, string):
        return urwid.Text(('info_text', "%s" % string), align='left')

    def _left_title_text(self, string):
        return urwid.Text(('title_text', "%s" % string), align='left')

    def _center_title_text(self, string):
        return urwid.Text(('title_text', string), align='center')

    def _progress_bar(self, pct):
        return urwid.ProgressBar('pb_normal', 'pb_complete', current=pct,
                                 done=100)

    def _stat_line(self, label, value, unit=None):
        mu = [('label_text', " %s: " % label), ('info_text', "%s " % value)]
        if unit:
            mu.append(('unit_text', "%s " % unit))
        return urwid.Text(mu, align='center')

    ###########################################################################

    def _setup_loop_background(self, reactor):
        fill_widget = urwid.SolidFill()
        mapped_widget = urwid.AttrMap(fill_widget, 'background')
        event_loop = urwid.TwistedEventLoop(reactor=reactor)
        loop = urwid.MainLoop(mapped_widget, PALETTE,
                              event_loop=event_loop,
                              unhandled_input=self.exit_on_q)
        cols, rows = loop.screen.get_cols_rows()
        loop.screen.set_terminal_properties(colors=256)
        return loop

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    ###########################################################################

    def _fmt_timestamp(self, timestamp):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _fmt_seconds(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return "%d min %d sec" % (m, s)

    ###########################################################################

    def _wrap_box(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'panel_box')

    def _wrap_box_alt(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'panel_box_alt')

    def _wrap_box_alt_2(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'panel_box_alt_2')

    def _wrap_box_alt_3(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'panel_box_alt_3')

    def _wrap_box_alt_4(self, widget, title):
        lb = urwid.LineBox(widget, title=title)
        f = urwid.Filler(lb)
        return urwid.AttrMap(lb, 'panel_box_alt_4')

    def _wrap_filler(self, widget):
        f = urwid.Filler(widget)
        return urwid.AttrMap(f, 'background')

    def _list_box(self, widgets):
        lb = urwid.ListBox(widgets)
        return urwid.AttrMap(lb, 'background')

    ###########################################################################

    def _fee_estimate_widget(self):
        if 'fee_estimate' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no fee estimates)")
        if 'fee_estimate_eco' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no eco fee estimates)")

        blocks = sorted(self.info['fee_estimate'].keys())

        b_row = [" Blks "]
        b_row += [str(b) for b in blocks]

        c_row = [" Norm "]
        c_row += [str(int(round(self.info['fee_estimate'][b]))) for b in
                  blocks]

        e_row = [" Econ "]
        e_row += [str(int(round(self.info['fee_estimate_eco'][b]))) for b in
                  blocks]

        b_strs = []
        c_strs = []
        e_strs = []
        for i in range(len(blocks) + 1):
            b = b_row[i]
            c = c_row[i]
            e = e_row[i]
            width = max(len(b), len(c), len(e))
            fmt = "%%%ds" % width
            b_strs.append(fmt % b)
            c_strs.append(fmt % c)
            e_strs.append(fmt % e)

        b_str = self._center_title_text(" ".join(b_strs) + " ")
        c_str = self._center_info_text_2(" ".join(c_strs) + " ")
        e_str = self._center_info_text_2(" ".join(e_strs) + " ")
        lines = [b_str, c_str, e_str]

        return self._wrap_box_alt_2(urwid.Pile(lines), "Fee Estimates (sat/byte)")

    def _bitcoind_widget(self):
        if 'net_connections' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no bitcoind data)")
        v = self._center_info_text("%s" % self.info['net_version'])
        c = self._stat_line("Peers", str(self.info['net_connections']))
        lines = [v, c]
        return self._wrap_box_alt(urwid.Pile(lines), "bitcoind")

    def _c_lightning_widget(self):
        if 'ln_version' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no lightning node data)")
        a = self._stat_line("Alias", self.info['ln_alias'])
        v = self._stat_line("Version", self.info['ln_version'])
        p = self._stat_line("Peers", self.info['ln_num_peers'])
        lines = [a, v, p]
        return self._wrap_box_alt(urwid.Pile(lines), "c-lightning")

    def _daemon_widget(self):
        b = self._bitcoind_widget()
        l = self._c_lightning_widget()

        lines = [b, l]
        return self._wrap_box_alt(urwid.Pile(lines), "Daemons")


    def _block_id_widget(self):
        h = self._stat_line("Height", str(self.info['block_height']))
        bn = self._stat_line("Name", self.info['block_name'])
        arrival = self._fmt_timestamp(self.info['block_arrival_time'])
        at = self._stat_line("Arrive Time", arrival, "UTC")
        miner = self._fmt_timestamp(self.info['block_timestamp'])
        t = self._stat_line("Miner Time", miner, "UTC")
        lines = [h, bn, at, t]
        return self._wrap_box_alt_2(urwid.Pile(lines), "Block ID")


    def _block_stat_widget(self):
        tx = self._stat_line("In Block",
                             "{:,}".format(self.info['block_n_txes']),
                             "txs")

        s = self._stat_line("Block Size",
                            "{:,}".format(self.info['block_size']),
                            "bytes")
        w = self._stat_line("Block Weight",
                            "{:,}".format(self.info['block_weight']),
                            "bytes")
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._center_info_text("%s since last block" %
                                   self._fmt_seconds(elapsed))
        lines = [tx, s, w, e]
        return self._wrap_box_alt_2(urwid.Pile(lines), "Block Stats")

    def _block_widget(self):
        if 'block_name' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no block data)")
        i = self._block_id_widget()
        s = self._block_stat_widget()
        lines = [i, s]
        return self._wrap_box_alt_2(urwid.Pile(lines), "")

    def _phrase_widget(self):
        if 'block_phrase' not in self.info:
            return self._wrap_box_alt_4(urwid.Pile([]), "(no block data)")
        p = self._center_info_text(self.info['block_phrase'])
        lines = [p]
        return self._wrap_box_alt_4(urwid.Pile(lines), "")

    def _ram_widget(self):
        if 'mempool_txs' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no mempool data)")
        if 'mem_total' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no ram data)")
        r = self._stat_line("RAM Total", "{:,}".format(self.info['mem_total']),
                             "bytes")
        ru = self._progress_bar(self.info['mem_used_pct'])
        t = self._stat_line("Mempool",
                            "{:,}".format(self.info['mempool_txs']),
                            "txs")
        b = self._stat_line("Mempool Size",
                            "{:,}".format(self.info['mempool_bytes']),
                            "bytes")
        mu = self._progress_bar(self.info['mempool_percent'])

        lines = [r, ru, t, b, mu]
        return self._wrap_box(urwid.Pile(lines), "RAM")

    def _net_widget(self):
        if 'net_send' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no network data)")
        s = self._stat_line("Send",
                            "{:,}".format(self.info['net_send']),
                            "byte/s")
        r = self._stat_line("Recv",
                            "{:,}".format(self.info['net_recv']),
                            "byte/s")
        lines = []
        if 'ip_address' in self.info:
            i = self._stat_line("LAN IP", self.info['ip_address'])
            lines = [s, r, i]
        else:
            lines = [s, r]

        return self._wrap_box(urwid.Pile(lines), "Network")

    def _disk_widget(self):
        if 'disk_read' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no disk data)")
        rd = self._stat_line("Read",
                             "{:,}".format(self.info['disk_read']),
                             "byte/s")
        wt = self._stat_line("Write",
                             "{:,}".format(self.info['disk_write']),
                             "byte/s")
        b = self._stat_line("Blockchain",
                            "{:,}".format(self.info['dir_size']),
                            "bytes")
        lines = [rd, wt, b]
        return self._wrap_box(urwid.Pile(lines), "Disk")

    def _cpu_widget(self):
        if 'cpu_pct' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no cpu data)")
        lines = []
        for cpu in self.info['cpu_pct']:
            lines.append(self._progress_bar(cpu))
        return self._wrap_box(urwid.Pile(lines),
                              "%d CPUs" % len(self.info['cpu_pct']))

    def _song_playing_widget(self):
        if 'song_playing_title' not in self.info:
            return self._wrap_box_alt_3(urwid.Pile([]), "(no song playing)")
        if not self.info['song_playing_title']:
            return self._wrap_box_alt_3(urwid.Pile([]), "(no song playing)")
        st = self._stat_line("Title", self.info['song_playing_title'])
        sa = self._stat_line("Artist", self.info['song_playing_artist'])
        lines = [st, sa]
        return self._wrap_box_alt_3(urwid.Pile(lines), "Now Playing")

    def _song_queue_widget(self):
        if 'queued_songs' not in self.info:
            return self._wrap_box_alt_3(urwid.Pile([]), "(no songs queued)")
        n = len(self.info['queued_songs'])
        if n == 0:
            return self._wrap_box_alt_3(urwid.Pile([]), "(no songs queued)")

        showing = min(n, 5)
        not_showing = (n - 5) if (n > 5) else 0

        lines = []
        songs = self.info['queued_songs']
        for i in range(showing):
            song = songs[i]
            t = self._center_info_text("%d) Title: %s" % (i + 1, song['title']))
            lines.append(t)
            a = self._center_info_text("   Artist: %s" % song['artist'])
            lines.append(a)
        if not_showing != 0:
            m = self._center_info_text("(%d more)" % not_showing)
            lines.append(m)
        return self._wrap_box_alt_3(urwid.Pile(lines), "Song Queue")

    ###########################################################################

    def _build_widgets(self):
        dae = self._daemon_widget()
        fee = self._fee_estimate_widget()
        blk = self._block_widget()

        r = self._ram_widget()
        n = self._net_widget()
        d = self._disk_widget()
        c = self._cpu_widget()

        sp = self._song_playing_widget()
        sq = self._song_queue_widget()

        ph = self._phrase_widget()

        col1 = self._list_box([dae, fee, ph])
        col2 = self._list_box([r, n, d, c])
        col3 = self._list_box([blk, sp, sq])
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
