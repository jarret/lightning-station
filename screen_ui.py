import time
from datetime import datetime, timezone
import pytz
import urwid
import textwrap
import json
from logger import log

LIGHT_ORANGE = "#fa0"
DARK_ORANGE = "#f60"

LIGHT_BLUE = "#0ff"
DARK_BLUE = "#00d"

LIGHT_GREEN = "#ad8"
DARK_GREEN = "#060"

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

GREY = DARK_GREY

NEUTRAL_GREY = 'g46'

PALETTE = [
           ('background', '', '', '', NEUTRAL_GREY, NEUTRAL_GREY),

           ('major_text', '', '', '', WHITE, BLACK),


           ('orange', '', '', '', BLACK, DARK_ORANGE),
           ('progress_orange_n', '', '', '', GREY, LIGHT_ORANGE),
           ('progress_orange_c',  '', '', '', LIGHT_ORANGE, GREY),
           ('orange_minor_text', '', '', '', LIGHT_ORANGE, BLACK),

           ('blue', '', '', '', WHITE, DARK_BLUE),
           ('progress_blue_n', '', '', '', GREY, LIGHT_BLUE),
           ('progress_blue_c',  '', '', '', LIGHT_BLUE, GREY),
           ('blue_minor_text', '', '', '', LIGHT_BLUE, BLACK),

           ('green', '', '', '', WHITE, DARK_GREEN),
           ('progress_green_n', '', '', '', GREY, LIGHT_GREEN),
           ('progress_green_c',  '', '', '', LIGHT_GREEN, GREY),
           ('green_minor_text', '', '', '', LIGHT_GREEN, BLACK),

           ('red', '', '', '', WHITE, DARK_RED),
           ('progress_red_n', '', '', '', GREY, LIGHT_RED),
           ('progress_red_c',  '', '', '', LIGHT_RED, GREY),
           ('red_minor_text', '', '', '', LIGHT_RED, BLACK),

           ('purple', '', '', '', WHITE, DARK_PURPLE),
           ('progress_purple_n', '', '', '', GREY, LIGHT_PURPLE),
           ('progress_purple_c',  '', '', '', LIGHT_PURPLE, GREY),
           ('purple_minor_text', '', '', '', LIGHT_PURPLE, BLACK),

           ('yellow', '', '', '', BLACK, DARK_YELLOW),
           ('progress_yellow_n', '', '', '', GREY, LIGHT_YELLOW),
           ('progress_yellow_c',  '', '', '', LIGHT_YELLOW, GREY),
           ('yellow_minor_text', '', '', '', LIGHT_YELLOW, BLACK),

           ('grey', '', '', '', WHITE, BLACK),
           ('progress_grey_n', '', '', '', GREY, LIGHT_GREY),
           ('progress_grey_c',  '', '', '', LIGHT_GREY, GREY),
           ('grey_minor_text', '', '', '', LIGHT_GREY, BLACK),

           ('bolt', '', '', '', DARK_YELLOW, BLACK),
           ('progress_bolt_n', '', '', '', BLACK, LIGHT_GREY),
           ('progress_bolt_c',  '', '', '', LIGHT_GREY, BLACK),
           ('bolt_minor_text', '', '', '', DARK_YELLOW, BLACK),

           ('coke', '', '', '', LIGHT_RED, BLACK),
           ('progress_coke_n', '', '', '', DARK_RED, DARK_GREY),
           ('progress_coke_c',  '', '', '', DARK_GREY, DARK_RED),
           ('coke_minor_text', '', '', '', LIGHT_RED, BLACK),
          ]


ORANGE_THEME = {
    'panel':      'orange',
    'progress_n': 'progress_orange_n',
    'progress_c': 'progress_orange_c',
    'major_text': 'major_text',
    'minor_text': 'orange_minor_text',
}

BLUE_THEME = {
    'panel':      'blue',
    'progress_n': 'progress_blue_n',
    'progress_c': 'progress_blue_c',
    'major_text': 'major_text',
    'minor_text': 'blue_minor_text',
}

GREEN_THEME = {
    'panel':      'green',
    'progress_n': 'progress_green_n',
    'progress_c': 'progress_green_c',
    'major_text': 'major_text',
    'minor_text': 'green_minor_text',
}

RED_THEME = {
    'panel':      'red',
    'progress_n': 'progress_red_n',
    'progress_c': 'progress_red_c',
    'major_text': 'major_text',
    'minor_text': 'red_minor_text',
}

PURPLE_THEME = {
    'panel':      'purple',
    'progress_n': 'progress_purple_n',
    'progress_c': 'progress_purple_c',
    'major_text': 'major_text',
    'minor_text': 'purple_minor_text',
}

YELLOW_THEME = {
    'panel':      'yellow',
    'progress_n': 'progress_yellow_n',
    'progress_c': 'progress_yellow_c',
    'major_text': 'major_text',
    'minor_text': 'yellow_minor_text',
}

GREY_THEME = {
    'panel':      'grey',
    'progress_n': 'progress_grey_n',
    'progress_c': 'progress_grey_c',
    'major_text': 'major_text',
    'minor_text': 'grey_minor_text',
}

BOLT_THEME = {
    'panel':      'bolt',
    'progress_n': 'progress_bolt_n',
    'progress_c': 'progress_bolt_c',
    'major_text': 'major_text',
    'minor_text': 'bolt_minor_text',
}

COKE_THEME = {
    'panel':      'coke',
    'progress_n': 'progress_coke_n',
    'progress_c': 'progress_coke_c',
    'major_text': 'major_text',
    'minor_text': 'coke_minor_text',
}


class ScreenUI(object):
    def __init__(self, reactor, console):
        self.loop = self._setup_loop_background(reactor)
        self.info = self._init_info()
        self._build_widgets()
        self.console = console

    ###########################################################################

    #def _init_info(self):
    #    return {'last_block': time.time()
    #           }

    def _init_info(self):
        return {'last_block': time.time(),
                #'song_playing_title': "Friday",
                #'song_playing_artist': "Rebecca Black",
                #'song_start_time': time.time(),
                #'song_length': 200.0,
                #'queued_songs': [
                #                 {'title': "Mo Money Mo Problems",
                #                  'artist': "Notorious B.I.G."},
                #                 {'title': "Hustlin'",
                #                  'artist': "Rick Ross"},
                #               ]
               }

    ###########################################################################

    def _center_major_text(self, string, theme):
        return urwid.Text((theme['major_text'], " %s " % string),
                          align='center')
    def _center_minor_text(self, string, theme):
        return urwid.Text((theme['minor_text'], " %s " % string),
                           align='center')

    def _progress_bar(self, pct, theme):
        return urwid.ProgressBar(theme['progress_n'], theme['progress_c'],
                                 current=pct, done=100)

    def _stat_line(self, label, value, unit, theme):
        mu = []
        if label != None:
            mu.append((theme['minor_text'], " %s: " % label))
        if value != None:
            mu.append((theme['major_text'], "%s " % value))
        if unit != None:
            mu.append((theme['minor_text'], "%s " % unit))
        return urwid.Text(mu, align='center')

    def _elapsed_line(self, elapsed, since, theme):
        a = (theme['major_text'], " " + self._fmt_seconds(elapsed))
        i = (theme['minor_text'], " since %s " % since)
        return urwid.Text([a, i], align='center')

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

    def _title_row(self, strs, theme):
        return self._center_minor_text(" ".join(strs), theme)

    def _row(self, strs, theme):
        t = (theme['minor_text'], " " + strs[0] + " ")
        m = (theme['major_text'], " ".join(strs[1:]) + " ")
        return urwid.Text([t, m], align='center')

    ###########################################################################

    def _fee_estimate_widget(self, theme):
        if 'fee_estimate' not in self.info:
            return self._dummy_box("(no fee estimates)", theme)
        if 'fee_estimate_eco' not in self.info:
            return self._dummy_box("(no eco fee estimates)", theme)

        blocks = sorted(self.info['fee_estimate'].keys())

        b_row = ["Blks"]
        b_row += [str(b) for b in blocks]

        c_row = ["Norm"]
        c_row += [str(int(round(self.info['fee_estimate'][b]))) for b in
                  blocks]

        e_row = ["Econ"]
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

        b_str = self._title_row(b_strs, theme)
        c_str = self._row(c_strs, theme)
        e_str = self._row(e_strs, theme)
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
        v = self._stat_line("Version", "%s" % self.info['net_version'], None,
                            theme)
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

    def _ln_channel_widget(self, theme):
        if 'ln_channels_pending' not in self.info:
            return self._dummy_box("(no lightning channel data)", theme)

        t_str = self._title_row(["%7s" % 'channel', "%7s" % 'pending',
                                 "%7s" % 'active', "%7s" % 'inactiv'], theme)

        p = self.info['ln_channels_pending']
        a = self.info['ln_channels_active']
        i = self.info['ln_channels_inactive']
        sep = self._center_minor_text("------------", theme)
        theirs = 1234677999 / 1000.0
        ours = 1234677999 / 1000.0
        onchain = int(round(1234677999 / 1000.0))
        c = sum([p, a, i])
        v_str = self._row(['%7d' % c, "%7d" % p, "%7d" % a, "%7d" % i], theme)

        o = self._stat_line("Node Owns", "%0.3f" % ours, 'satoshis', theme)
        t = self._stat_line("Peers Own", "%0.3f" % theirs, 'satoshis', theme)
        c = self._stat_line("On Chain", "%d" % onchain, 'satoshis', theme)

        lines = [t_str, v_str, sep, o, t, c]
        return self._line_pile_box(lines, "Lightning Peers", theme)

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
        tx = self._stat_line("Included",
                             "{:,}".format(self.info['block_n_txes']),
                             "txs", theme)

        s = self._stat_line("Block Size",
                            "{:,}".format(self.info['block_size']),
                            "bytes", theme)
        w = self._stat_line("Block Weight",
                            "{:,}".format(self.info['block_weight']),
                            "bytes", theme)
        elapsed = time.time() - self.info['block_arrival_time']
        e = self._elapsed_line(elapsed, "last block", theme)
        lines = [tx, s, w, e]
        return self._line_pile_box(lines, "Block Stats", theme)

    def _phrase_widget(self, theme):
        if 'block_phrase' not in self.info:
            return self._dummy_box("(no block data)", theme)
        wrapped = textwrap.wrap(self.info['block_phrase'], 28)
        lines = [self._center_major_text(l, theme) for l in wrapped]
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

    ############################################################################

    def _playing_line(self, title, artist, theme):
        tl = (theme['minor_text'], " Title: ")
        t = (theme['major_text'], title )
        al = (theme['minor_text'], " Artist: ")
        a = (theme['major_text'], artist + " ")
        return urwid.Text([tl, t, al, a], align='center')

    def _queued_line(self, song_idx, title, artist, theme):
        tl = (theme['minor_text'], " %d) " % song_idx)
        t = (theme['major_text'], title)
        al = (theme['minor_text'], " by ")
        a = (theme['major_text'], artist + " ")
        return urwid.Text([tl, t, al, a], align='center')

    def _playing_progress_line(self, start_time, length, theme):
        elapsed = time.time() - start_time
        p = (theme['major_text'], " %s " % (self._fmt_seconds(elapsed)))
        s = (theme['minor_text'], "of")
        d = (theme['major_text'], " %s " % (self._fmt_seconds(length)))
        return urwid.Text([p, s, d], align='center')

    def _playing_progress_bar(self, start_time, length, theme):
        elapsed = time.time() - start_time
        if elapsed > length:
            percent = 100.0
        else:
            percent = (elapsed / length) * 100.0
        return self._progress_bar(percent, theme)

    def _jukebox_widget(self, theme):
        if 'song_playing_title' not in self.info:
            return self._dummy_box("(no song playing)", theme)
        if not self.info['song_playing_title']:
            return self._dummy_box("(no song playing)", theme)
        p = self._playing_line(self.info['song_playing_title'],
                               self.info['song_playing_artist'], theme)
        pr = self._playing_progress_line(self.info['song_start_time'],
                                         self.info['song_length'], theme)
        pb = self._playing_progress_bar(self.info['song_start_time'],
                                        self.info['song_length'], theme)

        lines = [p, pr, pb]

        n = len(self.info['queued_songs'])
        if n == 0:
            return self._line_pile_box(lines, "Jukebox", theme)

        showing = min(n, 3)
        not_showing = (n - 3) if (n > 3) else 0
        s_lines = [self._center_minor_text("------------", theme)]
        songs = self.info['queued_songs']
        for i in range(showing):
            song = songs[i]
            a = self._queued_line(i + 1, song['title'], song['artist'], theme)
            s_lines.append(a)
        if not_showing != 0:
            m = self._center_major_text("(%d more)" % not_showing, theme)
            s_lines.append(m)
        return self._line_pile_box(lines + s_lines, "Jukebox", theme)

    ############################################################################

    def _build_widgets(self):
        d = self._disk_widget(YELLOW_THEME)
        n = self._net_widget(YELLOW_THEME)
        c = self._cpu_widget(BLUE_THEME)
        r = self._ram_widget(BLUE_THEME)
        ph = self._phrase_widget(RED_THEME)
        col1 = self._list_box([d, n, c, r, ph])

        bd = self._bitcoind_widget(ORANGE_THEME)
        bi = self._block_id_widget(GREEN_THEME)
        bs = self._block_stat_widget(GREEN_THEME)
        l = self._ledger_widget(PURPLE_THEME)
        fee = self._fee_estimate_widget(PURPLE_THEME)
        col2 = self._list_box([bd, bi, bs, l, fee])

        ld = self._c_lightning_widget(GREY_THEME)
        ch = self._ln_channel_widget(BOLT_THEME)
        j = self._jukebox_widget(COKE_THEME)

        col3 = self._list_box([ld, ch, j])

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
