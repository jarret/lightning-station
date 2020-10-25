# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
from fixed_draw import FreeDrawFont, HalfBlock5x6Font


class Widget():

    @staticmethod
    def btc_symb():
        w = urwid.BigText(('orange', "B"), FreeDrawFont())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 15)
        w = urwid.Filler(w, valign="middle")
        #w = urwid.AttrWrap(w, "orange")
        return w

    @staticmethod
    def itcoin():
        w = urwid.BigText(('orange', "ITCOIN!"),
                           urwid.font.HalfBlock7x7Font())
        w = urwid.Padding(w, align='left', width='clip')
        #w = urwid.SimpleFocusListWalker([w])
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign="middle")
        #w = urwid.AttrWrap(w, "orange")
        return w

    ###########################################################################

    def big_5x6(txt1):
        t, a, c = txt1
        w = urwid.BigText((c, t),
                          HalfBlock5x6Font())
        w = urwid.Padding(w, align=a, width='clip')
        w = urwid.ListBox([w])
        w = urwid.BoxAdapter(w, 7)
        w = urwid.Filler(w, valign='middle', top=2)
        return w

    def three_5x6(txt1, txt2, txt3):
        l = Widget.big_5x6(txt1)
        m = Widget.big_5x6(txt2)
        r = Widget.big_5x6(txt3)
        return [l, m, r]

    ###########################################################################

    @staticmethod
    def total_supply(total_supply):
        l = (" ~ ", 'right', 'orange_minor_text')
        totalstr = " {:,} ".format(total_supply)
        c = (totalstr, 'center', 'major_text')
        r = (" total BTC ", 'left', 'orange_minor_text')
        #s1 = Widget.total_supply_1()
        #s2 = Widget.total_supply_2(total_supply)
        #s3 = Widget.total_supply_3()

        s1, s2, s3 = Widget.three_5x6(l, c, r)

        w = urwid.Columns([(15, s1), (90, s2), (40, s3)])
        #w = urwid.Filler(w, top=1, bottom=1)
        return w
