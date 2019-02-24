import urwid
from datetime import datetime, timezone
import pytz
import json
import time
from logger import log

LIGHT_ORANGE = "#fa0"
DARK_ORANGE = "#f80"

LIGHT_BLUE = "#0ff"
DARK_BLUE = "#00d"

LIGHT_GREEN = "#0f0"
DARK_GREEN = "#080"

LIGHT_RED = "#f68"
DARK_RED = "#d00"

LIGHT_PURPLE = "#d6a"
DARK_PURPLE = "#a0f"

LIGHT_YELLOW = "#ff6"
DARK_YELLOW = "#fd0"

BLACK = "g0"
WHITE = "g100"

LIGHT_GREY = "g82"
DARK_GREY = "g19"

PALETTE = [
           ('background', '', '', '', 'g38', "g38"),

           ('emph_text', '', '', '', WHITE, BLACK),

           ('title_text', '', '', '', 'g78', BLACK),
           ('unit_text', '', '', '', 'g78', BLACK),
           ('label_text', '', '', '', 'g78', BLACK),

           ('orange', '', '', '', BLACK, DARK_ORANGE),
           ('progress_orange_n', '', '', '', 'g19', LIGHT_ORANGE),
           ('progress_orange_c',  '', '', '', LIGHT_ORANGE, 'g19'),

           ('blue', '', '', '', WHITE, DARK_BLUE),
           ('progress_blue_n', '', '', '', 'g19', LIGHT_BLUE),
           ('progress_blue_c',  '', '', '', LIGHT_BLUE, 'g19'),

           ('green', '', '', '', WHITE, DARK_GREEN),
           ('progress_green_n', '', '', '', 'g19', LIGHT_GREEN),
           ('progress_green_c',  '', '', '', LIGHT_GREEN, 'g19'),

           ('red', '', '', '', WHITE, DARK_RED),
           ('progress_red_n', '', '', '', 'g19', LIGHT_RED),
           ('progress_red_c',  '', '', '', LIGHT_RED, 'g19'),

           ('purple', '', '', '', WHITE, DARK_PURPLE),
           ('progress_purple_n', '', '', '', 'g19', LIGHT_PURPLE),
           ('progress_purple_c',  '', '', '', LIGHT_PURPLE, 'g19'),

           ('yellow', '', '', '', BLACK, DARK_YELLOW),
           ('progress_yellow_n', '', '', '', 'g19', LIGHT_YELLOW),
           ('progress_yellow_c',  '', '', '', LIGHT_YELLOW, 'g19'),

           ('grey', '', '', '', WHITE, DARK_GREY),
           ('progress_grey_n', '', '', '', 'g19', LIGHT_GREY),
           ('progress_grey_c',  '', '', '', LIGHT_GREY, 'g19'),
          ]


ORANGE_THEME = {
    'panel':      'orange',
    'progress_n': 'progress_orange_n',
    'progress_c': 'progress_orange_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

BLUE_THEME = {
    'panel':      'blue',
    'progress_n': 'progress_blue_n',
    'progress_c': 'progress_blue_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

GREEN_THEME = {
    'panel':      'green',
    'progress_n': 'progress_green_n',
    'progress_c': 'progress_green_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

RED_THEME = {
    'panel':      'red',
    'progress_n': 'progress_red_n',
    'progress_c': 'progress_red_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

PURPLE_THEME = {
    'panel':      'purple',
    'progress_n': 'progress_purple_n',
    'progress_c': 'progress_purple_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

YELLOW_THEME = {
    'panel':      'yellow',
    'progress_n': 'progress_yellow_n',
    'progress_c': 'progress_yellow_c',
    'emph_text':  'emph_text',
    'title_text': 'title_text',
    'label_text': 'label_text',
    'unit_text':  'unit_text',
}

GREY_THEME = {
    'panel':      'grey',
    'progress_n': 'progress_grey_n',
    'progress_c': 'progress_grey_c',
    'emph_text':  'emph_text',
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

    def _center_emph_text(self, string, theme):
        return urwid.Text((theme['emph_text'], " %s " % string), align='center')

    def _center_emph_text_2(self, string, theme):
        return urwid.Text((theme['emph_text'], "%s" % string), align='center')

    def _center_title_text(self, string, theme):
        return urwid.Text((theme['title_text'], string), align='center')

    def _progress_bar(self, pct, theme):
        return urwid.ProgressBar(theme['progress_n'], theme['progress_c'],
                                 current=pct, done=100)

    def _stat_line(self, label, value, unit, theme):
        mu = []
        if label != None:
            mu.append((theme['label_text'], " %s: " % label))
        if value != None:
            mu.append((theme['emph_text'], "%s " % value))
        if unit != None:
            mu.append((theme['unit_text'], "%s " % unit))
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

        b_str = self._center_title_text(" ".join(b_strs) + " ", theme)
        c_str = self._center_emph_text(" ".join(c_strs) + " ", theme)
        e_str = self._center_emph_text(" ".join(e_strs) + " ", theme)
        lines = [b_str, c_str, e_str]

        return self._line_pile_box(lines, "Fee Estimates (sat/byte)", theme)

    def _ledger_widget(self, theme):
        if 'dir_size' not in self.info:
            return self._dummy_box("(no ledger data)", theme)
        if 'mempool_txs' not in self.info:
            return self._dummy_box("(no mempool data)", theme)

        t = self._stat_line("Mempool",
                            "{:,}".format(self.info['mempool_txs']),
                            "txs", theme)
        s = self._stat_line("Mempool Size",
                            "{:,}".format(self.info['mempool_bytes']),
                            "bytes", theme)
        m = self._stat_line("Max Mempool",
                            "{:,}".format(self.info['mempool_max']),
                            "bytes", theme)
        mu = self._progress_bar(self.info['mempool_percent'], theme)
        b = self._stat_line("Blockchain",
                            "{:,}".format(self.info['dir_size']),
                            "bytes", theme)
        lines = [t, s, m, mu, b]
        return self._line_pile_box(lines, "Ledger", theme)

    def _bitcoind_widget(self, theme):
        if 'net_connections' not in self.info:
            return self._dummy_box("(no bitcoind data)", theme)
        v = self._center_emph_text("%s" % self.info['net_version'], theme)
        c = self._stat_line("Peers", str(self.info['net_connections']), None,
                            theme)
        lines = [v, c]
        return self._line_pile_box(lines, "bitcoind", theme)

    def _c_lightning_widget(self, theme):
        if 'ln_version' not in self.info:
            return self._dummy_box("(no lightning node data)", theme)
        a = self._stat_line("Alias", self.info['ln_alias'], None, theme)
        v = self._stat_line("Version", self.info['ln_version'], None, theme)
        p = self._stat_line("Peers", self.info['ln_num_peers'], None, theme)
        lines = [a, v, p]
        return self._line_pile_box(lines, "c-lightning", theme)

    def _block_id_widget(self, theme):
        if 'block_name' not in self.info:
            return self._dummy_box("(no block data)", theme)
        h = self._stat_line("Height", str(self.info['block_height']), None,
                            theme)
        bn = self._stat_line("Name", self.info['block_name'], None, theme)
        arrival = self._fmt_timestamp(self.info['block_arrival_time'])
        at = self._stat_line("Arrive Time", arrival, None, theme)
        miner = self._fmt_timestamp(self.info['block_timestamp'])
        t = self._stat_line("Miner Time", miner, None, theme)
        lines = [h, bn, at, t]
        return self._line_pile_box(lines, "Block ID", theme)


    def _block_stat_widget(self, theme):
        if 'block_n_txes' not in self.info:
            return self._dummy_box("(no block data)", theme)
        tx = self._stat_line("In Block",
                             "{:,}".format(self.info['block_n_txes']),
                             "txs", theme)

        s = self._stat_line("Block Size",
                            "{:,}".format(self.info['block_size']),
                            "bytes", theme)
        w = self._stat_line("Block Weight",
                            "{:,}".format(self.info['block_weight']),
                            "bytes", theme)
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._center_emph_text("%s since last block" %
                                   self._fmt_seconds(elapsed), theme)
        lines = [tx, s, w, e]
        return self._line_pile_box(lines, "Block Stats", theme)

    def _phrase_widget(self, theme):
        if 'block_phrase' not in self.info:
            return self._dummy_box("(no block data)", theme)
        p = self._center_emph_text(self.info['block_phrase'], theme)
        lines = [p]
        return self._line_pile_box(lines, "", theme)

    def _ram_widget(self, theme):
        if 'mem_total' not in self.info:
            return self._dummy_box("(no ram data)", theme)

        r = self._stat_line("RAM Total", "{:,}".format(self.info['mem_total']),
                            "bytes", theme)
        u = self._stat_line("RAM Used", "{:,}".format(self.info['mem_used']),
                            "bytes", theme)
        up = self._progress_bar(self.info['mem_used_pct'], theme)

        lines = [r, u, up]
        return self._line_pile_box(lines, "RAM", theme)

    def _net_widget(self, theme):
        if 'net_send' not in self.info:
            return self._dummy_box("(no network data)", theme)
        s = self._stat_line("Send",
                            "{:,}".format(self.info['net_send']),
                            "byte/s", theme)
        r = self._stat_line("Recv",
                            "{:,}".format(self.info['net_recv']),
                            "byte/s", theme)
        lines = []
        if 'ip_address' in self.info:
            i = self._stat_line("LAN IP", self.info['ip_address'], None, theme)
            lines = [i, s, r]
        else:
            lines = [s, r]
        return self._line_pile_box(lines, "Network", theme)

    def _disk_widget(self, theme):
        if 'disk_read' not in self.info:
            return self._dummy_box("(no disk data)", theme)
        rd = self._stat_line("Read",
                             "{:,}".format(self.info['disk_read']),
                             "byte/s", theme)
        wt = self._stat_line("Write",
                             "{:,}".format(self.info['disk_write']),
                             "byte/s", theme)
        lines = [rd, wt]
        return self._line_pile_box(lines, "Disk", theme)

    def _cpu_widget(self, theme):
        if 'cpu_pct' not in self.info:
            return self._dummy_box("(no cpu data)", theme)
        lines = []
        for cpu in self.info['cpu_pct']:
            lines.append(self._progress_bar(cpu, theme))
        title = "%d CPUs" % len(self.info['cpu_pct'])
        return self._line_pile_box(lines, title, theme)

    def _song_playing_widget(self, theme):
        if 'song_playing_title' not in self.info:
            return self._dummy_box("(no song playing)", theme)
        if not self.info['song_playing_title']:
            return self._dummy_box("(no song playing)", theme)
        st = self._stat_line("Title", self.info['song_playing_title'], None,
                             theme)
        sa = self._stat_line("Artist", self.info['song_playing_artist'], None,
                             theme)
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
            t = self._center_emph_text("%d) Title: %s" % (i + 1, song['title']),
                                       theme)
            lines.append(t)
            a = self._center_emph_text("   Artist: %s" % song['artist'], theme)
            lines.append(a)
        if not_showing != 0:
            m = self._center_emph_text("(%d more)" % not_showing, theme)
            lines.append(m)
        return self._line_pile_box(lines, "Song Queue", theme)

    ###########################################################################

    def _build_widgets(self):
        ph = self._phrase_widget(YELLOW_THEME)
        bd = self._bitcoind_widget(GREY_THEME)
        ld = self._c_lightning_widget(GREY_THEME)
        sp = self._song_playing_widget(BLUE_THEME)
        sq = self._song_queue_widget(BLUE_THEME)

        col1 = self._list_box([ph, bd, ld, sp, sq])

        bi = self._block_id_widget(ORANGE_THEME)
        bs = self._block_stat_widget(ORANGE_THEME)
        l = self._ledger_widget(PURPLE_THEME)
        fee = self._fee_estimate_widget(PURPLE_THEME)
        col2 = self._list_box([bi, bs, l, fee])

        c = self._cpu_widget(RED_THEME)
        r = self._ram_widget(RED_THEME)
        d = self._disk_widget(GREEN_THEME)
        n = self._net_widget(GREEN_THEME)
        col3 = self._list_box([c, r, d, n])

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
