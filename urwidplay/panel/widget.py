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

    ###########################################################################

#    def big_5x6(txt1):
#        t, a, c = txt1
#        w = urwid.BigText((c, t),
#                          HalfBlock5x6Font())
#        w = urwid.Padding(w, align=a, width='clip')
#        w = urwid.ListBox([w])
#        w = urwid.BoxAdapter(w, 6)
#        w = urwid.Filler(w, valign='top', top=1)
#        w = urwid.Padding(w)
#        return w
#
#    def three_5x6(txt1, txt2, txt3):
#        l = Widget.big_5x6(txt1)
#        m = Widget.big_5x6(txt2)
#        r = Widget.big_5x6(txt3)
#        return [l, m, r]
#
#    ###########################################################################
#
#    @staticmethod
#    def total_supply(total_supply):
#        l = (" ~ ", 'right', 'orange_minor_text')
#        totalstr = " {:,} ".format(total_supply)
#        c = (totalstr, 'center', 'major_text')
#        r = (" total BTC ", 'left', 'orange_minor_text')
#        s1, s2, s3 = Widget.three_5x6(l, c, r)
#        w = urwid.Columns([(15, s1), (90, s2), (40, s3)])
#        #w = urwid.Padding(w, align='center')
#        return w
#
#    @staticmethod
#    def mkt_cap(mkt_cap):
#        l = (" Cap:  $", 'right', 'dark_red_minor_text')
#        totalstr = " {:,} ".format(mkt_cap)
#        c = (totalstr, 'center', 'major_text')
#        r = (" CAD ", 'left', 'dark_red_minor_text')
#        s1, s2, s3 = Widget.three_5x6(l, c, r)
#        w = urwid.Columns([(30, s1), (95, s2), (20, s3)])
#        #w = urwid.Padding(w, align='center')
#        return w
#
#    @staticmethod
#    def price(price):
#        l = ("  $ ", 'right', 'dark_red_minor_text')
#        totalstr = " {:,} ".format(price)
#        c = (totalstr, 'center', 'major_text')
#        r = (" CAD per BTC ", 'left', 'dark_red_minor_text')
#        s1, s2, s3 = Widget.three_5x6(l, c, r)
#        w = urwid.Columns([(20, s1), (35, s2), (50, s3)])
#        #w = urwid.Padding(w, align='center')
#        return w

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
