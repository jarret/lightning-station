import urwid
from datetime import datetime, timezone
import pytz
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
           ('info_text', '', '', '', '#fff', 'g7'),
           ('background', '', '', '', 'g7', "g7"),
           ('panel_box', '', '', '', 'g0', PANEL),
           ('panel_box_alt', '', '', '', 'g0', PANEL_ALT),
           ('panel_box_alt_2', '', '', '', 'g0', PANEL_ALT_2),
           ('panel_box_alt_3', '', '', '', 'g0', PANEL_ALT_3),
           ('panel_box_alt_4', '', '', '', 'g0', PANEL_ALT_4),
           ('title_text', '', '', '', 'g78', 'g7'),
           ('unit_text', '', '', '', 'g78', 'g7'),
           ('label_text', '', '', '', 'g78', 'g7'),
           ('pb_normal', '', '', '', 'g19', BACK),
           ('pb_complete',  '', '', '', BACK, 'g19'),

           ('orange', '', '', '', 'g0', '#fa0'),
           ('progress_orange_n', '', '', '', 'g19','#fa0'),
           ('progress_orange_c',  '', '', '','#fa0', 'g19'),

           ('blue', '', '', '', 'g0', '#0ad'),
           ('progress_blue_n', '', '', '', 'g19', '#0ad'),
           ('progress_blue_c',  '', '', '', '#0ad', 'g19'),
          ]


ORANGE_THEME = {
    'panel':      'orange',
    'progress_n': 'progress_orange_n',
    'progress_c': 'progress_orange_c',
    'info_text':  'info_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

BLUE_THEME = {
    'panel':      'blue',
    'progress_n': 'progress_blue_n',
    'progress_c': 'progress_blue_c',
    'info_text':  'info_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}


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
        dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone('US/Mountain'))
        return dt.strftime('%b %d, %H:%M:%S')

    def _fmt_seconds(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return "%d min %d sec" % (m, s)

    ###########################################################################

    def _wrap_box(self, widget, title, theme=ORANGE_THEME):
        lb = urwid.LineBox(widget, title=title)
        return urwid.AttrMap(lb, theme['panel'])

    def _dummy_box(self, title, theme):
        return self._wrap_box(urwid.Pile([]), title, theme)

    def _line_pile_box(self, lines, title, theme):
        return self._wrap_box(urwid.Pile(lines), title, theme)

    def _list_box(self, widgets):
        lb = urwid.ListBox(widgets)
        return urwid.AttrMap(lb, 'background')

    ###########################################################################

    def _fee_estimate_widget(self, theme):
        if 'fee_estimate' not in self.info:
            return self._dummy_box("(no fee estimates)", theme)
        if 'fee_estimate_eco' not in self.info:
            return self._dummy_box("(no eco fee estimates)", theme)

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

        return self._line_pile_box(lines, "Fee Estimates (sat/byte)", theme)

    def _ledger_widget(self, theme):
        if 'dir_size' not in self.info:
            return self._dummy_box("(no ledger data)", theme)
        if 'mempool_txs' not in self.info:
            return self._dummy_box("(no mempool data)", theme)

        t = self._stat_line("Mempool",
                            "{:,}".format(self.info['mempool_txs']),
                            "txs")
        s = self._stat_line("Mempool Size",
                            "{:,}".format(self.info['mempool_bytes']),
                            "bytes")
        m = self._stat_line("Max Mempool",
                            "{:,}".format(self.info['mempool_max']),
                            "bytes")
        mu = self._progress_bar(self.info['mempool_percent'])
        b = self._stat_line("Blockchain",
                            "{:,}".format(self.info['dir_size']),
                            "bytes")
        lines = [t, s, m, mu, b]
        return self._line_pile_box(lines, "Ledger", theme)

    def _bitcoind_widget(self, theme):
        if 'net_connections' not in self.info:
            return self._dummy_box("(no bitcoind data)", theme)
        v = self._center_info_text("%s" % self.info['net_version'])
        c = self._stat_line("Peers", str(self.info['net_connections']))
        lines = [v, c]
        return self._line_pile_box(lines, "bitcoind", theme)

    def _c_lightning_widget(self, theme):
        if 'ln_version' not in self.info:
            return self._dummy_box("(no lightning node data)", theme)
        a = self._stat_line("Alias", self.info['ln_alias'])
        v = self._stat_line("Version", self.info['ln_version'])
        p = self._stat_line("Peers", self.info['ln_num_peers'])
        lines = [a, v, p]
        return self._line_pile_box(lines, "c-lightning", theme)

    def _block_id_widget(self, theme):
        if 'block_name' not in self.info:
            return self._dummy_box("(no block data)", theme)
        h = self._stat_line("Height", str(self.info['block_height']))
        bn = self._stat_line("Name", self.info['block_name'])
        arrival = self._fmt_timestamp(self.info['block_arrival_time'])
        at = self._stat_line("Arrive Time", arrival)
        miner = self._fmt_timestamp(self.info['block_timestamp'])
        t = self._stat_line("Miner Time", miner)
        lines = [h, bn, at, t]
        return self._line_pile_box(lines, "Block ID", theme)


    def _block_stat_widget(self, theme):
        if 'block_n_txes' not in self.info:
            return self._dummy_box("(no block data)", theme)
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
        return self._line_pile_box(lines, "Block Stats", theme)

    def _phrase_widget(self, theme):
        if 'block_phrase' not in self.info:
            return self._dummy_box("(no block data)", theme)
        p = self._center_info_text(self.info['block_phrase'])
        lines = [p]
        return self._line_pile_box(lines, "", theme)

    def _ram_widget(self, theme):
        if 'mem_total' not in self.info:
            return self._dummy_box("(no ram data)", theme)

        r = self._stat_line("RAM Total", "{:,}".format(self.info['mem_total']),
                            "bytes")
        u = self._stat_line("RAM Used", "{:,}".format(self.info['mem_used']),
                            "bytes")
        up = self._progress_bar(self.info['mem_used_pct'])

        lines = [r, u, up]
        return self._line_pile_box(lines, "RAM", theme)

    def _net_widget(self, theme):
        if 'net_send' not in self.info:
            return self._dummy_box("(no network data)", theme)
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

        return self._line_pile_box(lines, "Network", theme)

    def _disk_widget(self, theme):
        if 'disk_read' not in self.info:
            return self._dummy_box("(no disk data)", theme)
        rd = self._stat_line("Read",
                             "{:,}".format(self.info['disk_read']),
                             "byte/s")
        wt = self._stat_line("Write",
                             "{:,}".format(self.info['disk_write']),
                             "byte/s")
        lines = [rd, wt]
        return self._line_pile_box(lines, "Disk", theme)

    def _cpu_widget(self, theme):
        if 'cpu_pct' not in self.info:
            return self._dummy_box("(no cpu data)", theme)
        lines = []
        for cpu in self.info['cpu_pct']:
            lines.append(self._progress_bar(cpu))
        title = "%d CPUs" % len(self.info['cpu_pct'])
        return self._line_pile_box(lines, title, theme)

    def _song_playing_widget(self, theme):
        if 'song_playing_title' not in self.info:
            return self._dummy_box("(no song playing)", theme)
        if not self.info['song_playing_title']:
            return self._dummy_box("(no song playing)", theme)
        st = self._stat_line("Title", self.info['song_playing_title'])
        sa = self._stat_line("Artist", self.info['song_playing_artist'])
        lines = [st, sa]
        return self._line_pile_box(lines, "Now Playing", theme)

    def _song_queue_widget(self, theme):
        if 'queued_songs' not in self.info:
            return self._dummy_box("(no songs queued)", theme)
        n = len(self.info['queued_songs'])
        if n == 0:
            return self._dummy_box("(no songs queued)", theme)

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
        return self._line_pile_box(lines, "Song Queue", theme)

    ###########################################################################

    def _build_widgets(self):
        bd = self._bitcoind_widget(ORANGE_THEME)
        ld = self._c_lightning_widget(BLUE_THEME)
        fee = self._fee_estimate_widget(ORANGE_THEME)
        bi = self._block_id_widget(BLUE_THEME)
        bs = self._block_stat_widget(ORANGE_THEME)

        r = self._ram_widget(BLUE_THEME)
        n = self._net_widget(ORANGE_THEME)
        d = self._disk_widget(BLUE_THEME)
        c = self._cpu_widget(ORANGE_THEME)

        sp = self._song_playing_widget(BLUE_THEME)
        sq = self._song_queue_widget(ORANGE_THEME)

        ph = self._phrase_widget(BLUE_THEME)
        l = self._ledger_widget(ORANGE_THEME)

        col1 = self._list_box([bd, ld, fee, ph, sp, sq])
        col2 = self._list_box([r, n, d, c])
        col3 = self._list_box([bi, bs, l])
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
