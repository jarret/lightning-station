# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import urwid
import logging
import traceback
import datetime

from twisted.internet.task import LoopingCall

from palette import PALETTE

from palette import ORANGE_THEME, BLUE_THEME, GREEN_THEME, RED_THEME
from palette import PURPLE_THEME, YELLOW_THEME, GREY_THEME, BOLT_THEME
from palette import SPARK_THEME, COKE_THEME, SPEARMINT_THEME


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

    def assemble_widgets(self):
        #bitcoin_font = urwid.font.HalfBlock5x4Font
        #bitcoin = urwid.BigText("Bitcoin", bitcoin_font)
        #bitcoin = urwid.AttrWrap(bitcoin, 'purple')
        #bitcoin = urwid.Filler(bitcoin, "middle", ('relative', 50))
        #bitcoin = urwid.Padding(bitcoin, ('relative', 50))
        #bitcoin = urwid.BoxAdapter(bitcoin, 7)

        #bigtext = urwid.BigText("Bitcoin", bitcoin_font)
        #bt = SwitchingPadding(bigtext, 'left', None)
        #bt = urwid.AttrWrap(bt, 'bigtext')
        #bt = urwid.Filler(bt, 'bottom', None, 7)
        #bt = urwid.BoxAdapter(bt, 7)


      # a = (ORANGE_THEME['major_text'], " asdfads ")
       #i = (ORANGE_THEME['minor_text'], " since %s ")
        #bitcoin_text = urwid.BoxAdapter(urwid.Pile([urwid.Text("hello")]), 7)



        #bitcoin = urwid.ListBox(urwid.SimpleFocusListWalker([
        #    urwid.Padding(
        #        urwid.BigText(('purple', "Bitcoin"), urwid.HalfBlock5x4Font()),
        #        width='clip')
        #]))

        bitcoin = urwid.BigText(('orange', " Bitcoin "),
                                urwid.font.HalfBlock7x7Font())
        bitcoin = urwid.Padding(bitcoin, align='center', width='clip')
        bitcoin = urwid.SimpleFocusListWalker([bitcoin])
        bitcoin = urwid.ListBox(bitcoin)
        bitcoin = urwid.BoxAdapter(bitcoin, 7)
        bitcoin = urwid.LineBox(bitcoin)
        bitcoin = urwid.AttrWrap(bitcoin, "orange")
        bitcoin = urwid.Filler(bitcoin, valign="top")

        pricestr = " $ %.2f " % self.info['price_btccad']
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

        pricetime_pile = urwid.Pile([price, tm])

        #row1 = bt
        row1 = urwid.Columns([bitcoin, pricetime_pile])
        #row1 = urwid.Columns([bitcoin_text])
        row1 = urwid.AttrMap(row1, "green")

        row2 = urwid.Columns([])
        row2 = urwid.AttrMap(row2, "blue")

        row3 = urwid.Columns([])
        row3 = urwid.AttrMap(row3, "purple")

        w = urwid.Pile([row1, row2, row3])
        #w = urwid.Pile([])
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
