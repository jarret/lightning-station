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

    def _assemble_header_row(self):
        btc_symb = Widget.btc_symb()
        itcoin = Widget.itcoin()
        subtitle = Widget.subtitle()
        bitcoin = urwid.Columns([(18, btc_symb), (40, itcoin), (100, subtitle)])

        total_supply = Widget.total_supply(self.info['total_supply'])
        title = urwid.Pile([('weight', 20, bitcoin),
                            ('weight', 10, total_supply)])

        price = Widget.price(self.info['price_btccad'])
        inv_price = Widget.inv_price(self.info['price_cadbtc'])
        mkt_cap_str = self.info['mkt_cap_cad']
        mkt_cap = Widget.mkt_cap(self.info['mkt_cap_cad'])
        #dt = Widget.date_and_time(time.time())

        c3 = urwid.Pile([(6, price), (6, inv_price), (6, mkt_cap)])
        c3 = urwid.Filler(c3)
        #c3 = urwid.LineBox(c3)

        row = urwid.Columns([(160, title), c3])
        row = urwid.AttrMap(row, "orange")
        return row

    def _assemble_middle_row(self):
        cpu = Widget.cpu_box(self.info['cpu_pcts'], BLUE_THEME)
        #cpu = urwid.Filler(cpu)
        ram = Widget.ram_box(self.info['mem_total'], self.info['mem_used'],
                             self.info['mem_used_pct'], BLUE_THEME)
        #ram = urwid.Filler(ram)

        syslist = urwid.ListBox([cpu, ram])
        #boxpile = urwid.Filler(boxpile)
        row = urwid.Columns([(30, syslist)])
        row = urwid.AttrMap(row, "spearmint_back")
        return row

    def _assemble_bottom_row(self):

        i = Widget.block_id_box(self.info['block_height'],
                                self.info['block_arrival_timestamp'],
                                self.info['block_timestamp'], GREEN_THEME)

        s = Widget.block_stat_box(self.info['block_n_txes'],
                                  self.info['block_size'],
                                  self.info['block_weight'],
                                  self.info['block_arrival_timestamp'],
                                  GREEN_THEME)

        blist = urwid.ListBox([i, s])
        row = urwid.Columns([(40, blist)])
        row = urwid.AttrMap(row, "coke_back")
        return row

    def assemble_widgets(self):
        header_row = self._assemble_header_row()
        middle_row = self._assemble_middle_row()
        bottom_row = self._assemble_bottom_row()

        w = urwid.Pile([header_row, middle_row, bottom_row])
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
