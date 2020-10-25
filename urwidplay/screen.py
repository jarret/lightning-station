# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import urwid
import logging
import traceback
import datetime

from twisted.internet.task import LoopingCall

from palette import PALETTE

from palette import ORANGE_THEME, BLUE_THEME, GREEN_THEME, RED_THEME
from palette import PURPLE_THEME, YELLOW_THEME, GREY_THEME, BOLT_THEME
from palette import SPARK_THEME, COKE_THEME, SPEARMINT_THEME

from fixed_draw import FreeDrawFont

from widget import Widget


BTC_SYMBOL = "₿"


class Screen():
    def __init__(self, info, reactor, console=False):
        self.console = console
        self.info = info
        self.reactor = reactor
        self.loop = self._setup_loop()
        self.draw_periodic = None


    def _setup_loop(self):
        w = self.assemble_widgets()
        event_loop = urwid.TwistedEventLoop(reactor=self.reactor)
        loop = urwid.MainLoop(w, PALETTE, event_loop=event_loop,
                              unhandled_input=self.handle_input)
        cols, rows = loop.screen.get_cols_rows()
        logging.info("cols: %s rows: %s" % (cols, rows))
        loop.screen.set_terminal_properties(colors=256)
        return loop

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        else:
            logging.info("got keypress: %s" % str(key))

    def _wrap_box(self, widget, title, theme=ORANGE_THEME):
        lb = urwid.LineBox(widget, title=title)
        return urwid.AttrMap(lb, theme['panel'])

    def _dummy_box(self, title, theme):
        return self._wrap_box(urwid.Pile([]), title, theme)

    def assemble_widgets2(self):
        symb = urwid.BigText(('orange', "B"),FreeDrawFont())
        symb = urwid.Padding(symb, align='left', width='clip')
        symb = urwid.SimpleFocusListWalker([symb])
        symb = urwid.ListBox(symb)
        symb = urwid.BoxAdapter(symb, 15)
        symb = urwid.Filler(symb, valign="top")
        symb = urwid.AttrWrap(symb, "orange")

        bitcoin = urwid.BigText(('orange', "ITCOIN! "),
                                urwid.font.HalfBlock7x7Font())
        bitcoin = urwid.Padding(bitcoin, align='left', width='clip')
        bitcoin = urwid.SimpleFocusListWalker([bitcoin])
        bitcoin = urwid.ListBox(bitcoin)
        bitcoin = urwid.BoxAdapter(bitcoin, 7)
        #bitcoin = urwid.LineBox(bitcoin)
        bitcoin = urwid.Filler(bitcoin, valign="bottom")
        bitcoin = urwid.AttrWrap(bitcoin, "orange")

        totalstr = " %.8f total BTC " % self.info['total_supply']
        total = urwid.BigText(('orange', totalstr),
                                urwid.font.HalfBlock5x4Font())
        total = urwid.Padding(total, align='center', width='clip')
        total = urwid.SimpleFocusListWalker([total])
        total = urwid.ListBox(total)
        total = urwid.BoxAdapter(total, 7)
        total = urwid.LineBox(total)
        total = urwid.AttrWrap(total, "orange")
        total = urwid.Filler(total, valign="top")



        pricestr = " $ %.2f CAD per BTC" % self.info['price_btccad']
        price = urwid.BigText(('purple', pricestr),
                                urwid.font.HalfBlock5x4Font())
        #price = urwid.Filler(price, valign="middle")
        price = urwid.Padding(price, align='center', width='clip')
        price = urwid.SimpleFocusListWalker([price])
        price = urwid.ListBox(price)
        price = urwid.BoxAdapter(price, 4)
        price = urwid.LineBox(price)
        price = urwid.AttrWrap(price, "purple")
        price = urwid.Filler(price, valign="top")

        capstr = "Mkt Cap: $ %.2f " % (self.info['price_btccad'] *
                                          self.info['total_supply'])
        cap = urwid.BigText(('purple', capstr),
                             urwid.font.HalfBlock5x4Font())
        #price = urwid.Filler(price, valign="middle")
        cap = urwid.Padding(cap, align='center', width='clip')
        cap = urwid.SimpleFocusListWalker([cap])
        cap = urwid.ListBox(cap)
        cap = urwid.BoxAdapter(cap, 4)
        cap = urwid.LineBox(cap)
        cap = urwid.AttrWrap(cap, "purple")
        cap = urwid.Filler(cap, valign="top")

        timestr = datetime.datetime.now().strftime(" %d/%m/%y %H:%M:%S ")
        tm = urwid.BigText(('purple', timestr),
                           urwid.font.HalfBlock5x4Font())
        tm = urwid.Padding(tm, align="center", width='clip')
        tm = urwid.SimpleFocusListWalker([tm])
        tm = urwid.ListBox(tm)
        tm = urwid.BoxAdapter(tm, 4)
        tm = urwid.LineBox(tm)
        tm = urwid.AttrWrap(tm, "purple")
        tm = urwid.Filler(tm, valign="bottom")

        pricetime_pile = urwid.Pile([price, cap, tm])

        bitcoin_pile = urwid.Pile([bitcoin, total])

        symb_pile = urwid.Pile([symb])
        #row1 = bt
        row1 = urwid.Columns([(18, symb_pile), bitcoin_pile, pricetime_pile])
        #row1 = urwid.Columns([bitcoin_text])
        row1 = urwid.AttrMap(row1, "green")

        row2 = urwid.Columns([])
        row2 = urwid.AttrMap(row2, "blue")

        row3 = urwid.Columns([])
        row3 = urwid.AttrMap(row3, "purple")

        w = urwid.Pile([row1, row2, row3])
        #w = urwid.Pile([])
        return w

    def assemble_widgets(self):
        btc_symb = Widget.btc_symb()
        itcoin = Widget.itcoin()
        subtitle = Widget.subtitle()
        bitcoin = urwid.Columns([(18, btc_symb), (40, itcoin), (100, subtitle)])

        total_supply = Widget.total_supply(self.info['total_supply'])
        title = urwid.Pile([(19, bitcoin), (6, total_supply)])

        price = Widget.price(self.info['price_btccad'])
        inv_price = Widget.inv_price(self.info['price_btccad'])
        mkt_cap_str = self.info['price_btccad'] * self.info['total_supply']
        mkt_cap = Widget.mkt_cap(mkt_cap_str)
        #dt = Widget.date_and_time(time.time())

        c3 = urwid.Pile([(6, price), (6, inv_price), (6, mkt_cap)])
        c3 = urwid.Filler(c3)
        #c3 = urwid.LineBox(c3)

        row1 = urwid.Columns([(160, title), c3])
        row1 = urwid.AttrMap(row1, "orange")

        row2 = urwid.Columns([])
        row2 = urwid.AttrMap(row2, "blue")

        row3 = urwid.Columns([])
        row3 = urwid.AttrMap(row3, "purple")

        w = urwid.Pile([row1, row2, row3])
        return w

    def draw_screen(self):
        logging.info("hello")
        try:
            w = self.assemble_widgets()
            self.loop.widget = w
            logging.info("drawww %s" % w)
            self.loop.draw_screen()
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(tb)
            print("poo")
            print("exept: %s" % e)

    def run(self):
        self.draw_periodic = LoopingCall(self.draw_screen)
        self.draw_periodic.start(1.0, now=False)
        self.loop.run()
