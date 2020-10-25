# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
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
        w = urwid.Filler(w, valign="top", top=3)
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
        totalstr = "{:,} ".format(total_supply)
        markup = [("orange_minor_text", " ~ "),
                  ("major_text", totalstr),
                  ("orange_minor_text", " total BTC ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def mkt_cap(mkt_cap):
        mkt_cap_str = "{:,} ".format(round(mkt_cap, 2))
        markup = [("dark_red_minor_text", " Mkt Cap: $ "),
                  ("major_text", mkt_cap_str),
                  ("dark_red_minor_text", " CAD ")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def price(price):
        pricestr = "{:,} ".format(round(price, 2))
        markup = [("dark_red_minor_text", " $ "),
                  ("major_text", pricestr),
                  ("dark_red_minor_text", " CAD "),
                  ("grey_minor_text", "per"),
                  ("orange_minor_text", " BTC")]
        w = Widget.big_5x6(markup, "center")
        return w

    @staticmethod
    def date_and_time(timestamp):
        timestr = datetime.fromtimestamp(timestamp).strftime(
            " %d/%m/%y %H:%M:%S ")
        markup = [("grey_minor_text", timestr)]
        w = Widget.big_5x6(markup, "center")
        return w
