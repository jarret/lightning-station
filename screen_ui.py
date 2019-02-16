import urwid
import datetime
import json
import time
from logger import log


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

    def _right_info_text(self, string):
        return urwid.Text(('info_text', " %s " % string), align='right')

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
        return urwid.AttrMap(lb, 'background')

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

        title_row = []
        title_row.append(self._center_title_text("Blocks"))
        title_row.append(self._center_title_text("Fee"))
        title_row.append(self._center_title_text("Eco"))

        title = urwid.GridFlow(title_row, 8, 0, 0, "center")
        lines = [title]

        for block in sorted(self.info['fee_estimate'].keys()):
            line = []
            con = self.info['fee_estimate'][block]
            eco = self.info['fee_estimate_eco'][block]

            line.append(self._right_info_text(str(block)))
            line.append(self._right_info_text("%0.2f" % (con)))
            line.append(self._right_info_text("%0.2f" % (eco)))

            lines.append(urwid.GridFlow(line, 8, 0, 0, "center"))

        return self._wrap_box(urwid.Pile(lines), "Daemon Fee Estimates")

    def _bitcoind_widget(self):
        if 'net_connections' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no bitcoind data)")
        v = self._center_info_text("%s" % self.info['net_version'])
        c = self._center_info_text("peers: %d" % self.info['net_connections'])
        lines = [v, c]
        return self._wrap_box(urwid.Pile(lines), "bitcoind")

    def _c_lightning_widget(self):
        if 'ln_version' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no lightning node data)")
        a = self._center_info_text("Alias %s" % self.info['ln_alias'])
        v = self._center_info_text("Version %s" % self.info['ln_version'])
        #p = self._center_info_text("Peers: %d" % self.info['ln_num_peers'])
        lines = [a, v]
        return self._wrap_box(urwid.Pile(lines), "c-lightning")

    def _daemon_widget(self):
        b = self._bitcoind_widget()
        l = self._c_lightning_widget()

        lines = [b, l]
        return self._wrap_box(urwid.Pile(lines), "Daemons")


    def _block_id_widget(self):
        h = self._center_info_text("Block Height: %d" %
                                    self.info['block_height'])
        bn = self._center_info_text("Block Name: %s" %
                                     self.info['block_name'])
        p = self._center_info_text(self.info['block_phrase'])
        arrival = self.info['block_arrival_time']
        at = self._center_info_text(
            "Arrival: %s" % self._fmt_timestamp(arrival))
        lines = [h, bn, p, at]
        return self._wrap_box(urwid.Pile(lines), "Block ID")

    def _block_stat_widget(self):
        tx = self._center_info_text(
            "TXs in Block: {:,}".format(self.info['block_n_txes']))

        s = self._center_info_text(
            "Block Size: {:,} bytes".format(self.info['block_size']))
        w = self._center_info_text(
            "Block Weight: {:,} bytes".format(self.info['block_weight']))
        t = self._center_info_text(
            "Timestamp: %s" % self._fmt_timestamp(self.info['block_timestamp']))
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._center_info_text("%s since last block" %
                                   self._fmt_seconds(elapsed))
        lines = [tx, s, w, t, e]
        return self._wrap_box(urwid.Pile(lines), "Block Stats")

    def _block_widget(self):
        if 'block_name' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no block data)")
        i = self._block_id_widget()
        s = self._block_stat_widget()
        lines = [i, s]
        return self._wrap_box(urwid.Pile(lines), "")

    def _ram_widget(self):
        if 'mempool_txs' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no mempool data)")
        if 'mem_total' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no ram data)")
        t = self._center_info_text(
            "Mempool TXs: {:,}".format(self.info['mempool_txs']))
        b = self._center_info_text("Mempool Bytes: {:,}".format(
            self.info['mempool_bytes']))
        mu = self._progress_bar('used', 'free', self.info['mempool_percent'])

        r = self._center_info_text(
            "RAM Total: {:,} bytes".format(self.info['mem_total']))
        ru = self._progress_bar('used', 'free', self.info['mem_used_pct'])
        lines = [t, b, mu, r, ru]
        return self._wrap_box(urwid.Pile(lines), "RAM")

    def _net_widget(self):
        if 'net_send' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no network data)")
        s = self._center_info_text(
            "Net Send: {:,} bytes/s".format(self.info['net_send']))
        r = self._center_info_text(
            "Net Recv: {:,} bytes/s".format(self.info['net_recv']))
        lines = []
        if 'ip_address' in self.info:
            i = self._center_info_text("LAN IP: %s" % self.info['ip_address'])
            lines = [s, r, i]
        else:
            lines = [s, r]

        return self._wrap_box(urwid.Pile(lines), "Network")

    def _disk_widget(self):
        if 'disk_read' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no disk data)")
        rd = self._center_info_text(
            "Disk Read: {:,} bytes/s".format(self.info['disk_read']))
        wt = self._center_info_text(
            "Disk Write: {:,} bytes/s".format(self.info['disk_write']))
        d = self._center_info_text(
            "Blockchain Dir: {:,} bytes".format(self.info['dir_size']))
        lines = [rd, wt, d]
        return self._wrap_box(urwid.Pile(lines), "Disk")

    def _cpu_widget(self):
        if 'cpu_pct' not in self.info:
            return self._wrap_box(urwid.Pile([]), "(no cpu data)")
        c = self._center_info_text("CPUs: %d" % len(self.info['cpu_pct']))
        lines = [c]
        for cpu in self.info['cpu_pct']:
            lines.append(self._progress_bar('used', 'free', cpu))
        return self._wrap_box(urwid.Pile(lines), "CPU")

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
            t = self._center_info_text("%d) Title: %s" % (i + 1, song['title']))
            lines.append(t)
            a = self._center_info_text("   Artist: %s" % song['artist'])
            lines.append(a)
        if not_showing != 0:
            m = self._center_info_text("(%d more)" % not_showing)
            lines.append(m)
        return self._wrap_box(urwid.Pile(lines), "Song Queue")

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

        col1 = self._list_box([dae, fee])
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
