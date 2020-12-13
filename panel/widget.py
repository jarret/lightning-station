# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
import time
import datetime
from datetime import datetime
from fixed_draw import FreeDrawFont, HalfBlock5x6Font


class Widget():

    @staticmethod
    def btc_symb():
        w = urwid.BigText(('orange', "B"), FreeDrawFont())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 15)
        w = urwid.Filler(w, valign="top")
        #w = urwid.AttrWrap(w, "orange")
        return w

    @staticmethod
    def itcoin():
        w = urwid.BigText(('orange', "ITCOIN"),
                           urwid.font.HalfBlock7x7Font())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        #w = urwid.AttrWrap(w, "orange")
        return w

    @staticmethod
    def subtitle_top():
        markup = [('orange', "A Peer-to-Peer")]
        w = urwid.BigText(markup,
                          urwid.font.HalfBlock5x4Font())
        w = urwid.Padding(w, align='center', width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        return w

    @staticmethod
    def subtitle_bottom():
        markup = [('orange', "Electronic Cash System")]
        w = urwid.BigText(markup,
                          urwid.font.HalfBlock5x4Font())
        w = urwid.Padding(w, align='center', width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        return w

    @staticmethod
    def subtitle():
        top = Widget.subtitle_top()
        bottom = Widget.subtitle_bottom()
        return urwid.Filler(urwid.Pile([(6, top), (6, bottom)]), top=2)

    def big_5x6(markup, align):
        w = urwid.BigText(markup, HalfBlock5x6Font())
        w = urwid.Padding(w, align=align, width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 6)
        w = urwid.Filler(w)
        w = urwid.Padding(w)
        return w

    ###########################################################################

    @staticmethod
    def total_supply(total_supply):
        totalstr = "{:,}".format(total_supply)
        markup = [("orange_minor_text", " ~ "),
                  ("major_text", totalstr),
                  ("grey_minor_text", " total"),
                  ("orange_minor_text", " BTC ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def mkt_cap(mkt_cap):
        mkt_cap_str = "{:,} ".format(int(mkt_cap))
        markup = [("grey_minor_text", " Mkt Cap:"),
                  ("dark_red_minor_text", " $ "),
                  ("major_text", mkt_cap_str),
                  ("dark_red_minor_text", " CAD ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def price(price):
        pricestr = "{:,.2f} ".format(round(price, 2))
        markup = [("dark_red_minor_text", " $ "),
                  ("major_text", pricestr),
                  ("dark_red_minor_text", " CAD "),
                  ("grey_minor_text", "per"),
                  ("orange_minor_text", " BTC ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def inv_price(price):
        price = round(price, 8)
        pricestr = " %0.8f" % price
        markup = [("orange_minor_text", " ~ "),
                  ("major_text", pricestr),
                  ("orange_minor_text", " BTC "),
                  ("grey_minor_text", "per"),
                  ("dark_red_minor_text", " CAD ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def date_and_time(timestamp):
        timestr = datetime.fromtimestamp(timestamp).strftime(
            " %d/%m/%y %H:%M:%S ")
        markup = [("grey_minor_text", timestr)]
        w = Widget.big_5x6(markup, "center")
        return w

    ###########################################################################

    @staticmethod
    def _wrap_box(widget, title, theme):
        lb = urwid.LineBox(widget, title=title)
        return urwid.AttrMap(lb, theme['panel'])

    @staticmethod
    def _dummy_box(title, theme):
        return Widget._wrap_box(urwid.Pile([]), title, theme)

    ###########################################################################

    @staticmethod
    def _progress_bar(pct, theme):
        return urwid.ProgressBar(theme['progress_n'], theme['progress_c'],
                                 current=pct, done=100)

    @staticmethod
    def _stat_line(label, value, unit, theme):
        mu = []
        if label != None:
            mu.append((theme['minor_text'], " %s: " % label))
        if value != None:
            mu.append((theme['major_text'], "%s " % value))
        if unit != None:
            mu.append((theme['minor_text'], "%s " % unit))
        return urwid.Text(mu, align='center')

    @staticmethod
    def _line_pile_box(lines, title, theme):
        return Widget._wrap_box(urwid.Pile(lines), title, theme)

    ###########################################################################

    @staticmethod
    def _fmt_seconds(seconds):
        m = seconds // 60
        s = seconds % 60
        return "%d min %d sec" % (m, s)

    @staticmethod
    def _fmt_timestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%b %d, %H:%M:%S')

    @staticmethod
    def _elapsed_line(elapsed, since, theme):
        a = (theme['major_text'], " " + Widget._fmt_seconds(elapsed))
        i = (theme['minor_text'], " since %s " % since)
        return urwid.Text([a, i], align='center')

    ###########################################################################
    def _center_major_text(string, theme):
        return urwid.Text((theme['major_text'], " %s " % string),
                          align='center')
    def _center_minor_text(string, theme):
        return urwid.Text((theme['minor_text'], " %s " % string),
                           align='center')

    @staticmethod
    def _title_row(strs, theme):
        return Widget._center_minor_text(" ".join(strs), theme)

    @staticmethod
    def _row(strs, theme):
        t = (theme['minor_text'], " " + strs[0] + " ")
        m = (theme['major_text'], " ".join(strs[1:]) + " ")
        return urwid.Text([t, m], align='center')


    ###########################################################################

    @staticmethod
    def cpu_box(cpu_pcts, theme):
        if cpu_pcts is None:
            return Widget._dummy_box("(no cpu data)", theme)
        lines = []
        for cpu in cpu_pcts:
            lines.append(Widget._progress_bar(cpu, theme))
        title = "%d CPUs" % len(cpu_pcts)
        return Widget._line_pile_box(lines, title, theme)

    @staticmethod
    def ram_box(mem_total, mem_used, mem_used_pct, theme):
        if mem_total is None:
            return Widget._dummy_box("(no ram data)", theme)

        r = Widget._stat_line("Total", "{:,}".format(mem_total),
                            "bytes", theme)
        u = Widget._stat_line("Used", "{:,}".format(mem_used),
                            "bytes", theme)
        up = Widget._progress_bar(mem_used_pct, theme)

        lines = [r, u, up]
        return Widget._line_pile_box(lines, "RAM", theme)


    @staticmethod
    def mempool_box(mempool_txes, mempool_bytes, mempool_max_used,
                    mempool_mem_used, theme):
        if mempool_txes is None:
            return Widget._dummy_box("(no block data)", theme)

        h = Widget._stat_line("Mempool Txes", "{:,}".format(mempool_txes),
                              None, theme)
        at = Widget._stat_line("Tx Bytes", "{:,}".format(mempool_bytes),
                               None, theme)
        m = Widget._stat_line("Max Mempool RAM",
                              "{:,}".format(mempool_max_used), None, theme)
        x = Widget._stat_line("RAM Used", "{:,}".format(mempool_mem_used),
                              None, theme)
        lines = [h, at, m, x]
        return Widget._line_pile_box(lines, "Mempool", theme)

    @staticmethod
    def estimates_box(fee_estimates, fee_estimates_eco, theme):
        blocks = sorted(fee_estimates.keys(), key=lambda x: int(x))

        b_row = ["Blks"]
        b_row += [str(b) for b in blocks]

        c_row = ["Norm"]
        c_row += [str(int(round(fee_estimates[b]))) for b in
                  blocks]

        e_row = ["Econ"]
        e_row += [str(int(round(fee_estimates_eco[b]))) for b in
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

        b_str = Widget._title_row(b_strs, theme)
        c_str = Widget._row(c_strs, theme)
        e_str = Widget._row(e_strs, theme)
        lines = [b_str, c_str, e_str]
        return Widget._line_pile_box(lines, "Fee Estimates (sat/byte)", theme)

    @staticmethod
    def block_id_box(block_height, block_arrival_timestamp, block_timestamp,
                     theme):
        if block_height is None:
            return Widget._dummy_box("(no block data)", theme)
        h = Widget._stat_line("Height", str(block_height), None, theme)
        arrival = Widget._fmt_timestamp(block_arrival_timestamp)
        at = Widget._stat_line("Arrive Time", arrival, None, theme)
        miner = Widget._fmt_timestamp(block_timestamp)
        t = Widget._stat_line("Miner Time", miner, None, theme)
        lines = [h, at, t]
        return Widget._line_pile_box(lines, "Block ID", theme)


    @staticmethod
    def block_stat_box(block_n_txes, block_size, block_weight,
                       block_arrival_timestamp, theme):
        if block_n_txes is None:
            return Widget._dummy_box("(no block data)", theme)
        tx = Widget._stat_line("Included",
                               "{:,}".format(block_n_txes),
                               "txs", theme)

        s = Widget._stat_line("Block Size",
                              "{:,}".format(block_size),
                              "bytes", theme)
        w = Widget._stat_line("Block Weight",
                              "{:,}".format(block_weight),
                              "bytes", theme)
        elapsed = time.time() - block_arrival_timestamp
        e = Widget._elapsed_line(elapsed, "last block", theme)
        lines = [tx, s, w, e]
        return Widget._line_pile_box(lines, "Block Stats", theme)