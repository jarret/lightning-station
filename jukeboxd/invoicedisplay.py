#!/usr/bin/env python3
# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import time
import logging
import textwrap

import RPi.GPIO as GPIO

from waveshare.epaper import Handshake
from waveshare.epaper import RefreshAndUpdate
from waveshare.epaper import SetPallet
from waveshare.epaper import FillRectangle
from waveshare.epaper import DisplayText
from waveshare.epaper import SetCurrentDisplayRotation
from waveshare.epaper import SetEnFontSize
from waveshare.epaper import ClearScreen

from qrdraw import QRDraw



class InvoiceDisplay(object):
    """
    Class for drawing soda invoices on the e-paper screen
    """
    def __init__(self, paper, mode=GPIO.BOARD, refresh_cb=None):
        self.paper = paper
        self.mode = mode
        self.refresh_cb = refresh_cb
        self._setup_display()

    def _handshake(self):
        #logging.info("handshake")
        start_time = time.time()
        self.paper.send(Handshake())
        #logging.info("handshake: %0.2f seconds" % (time.time() - start_time))

    def _set_pallet_black(self):
        # This is darker and good for text, but there is some bleed into
        # adjacent pixels on the grid.
        #logging.info("set pallet")
        start_time = time.time()
        self.paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))
        #logging.info("set pallet: %0.2f seconds" % (time.time() - start_time))

    def _set_pallet_gray(self):
        # this is the most accurate for staying in the pixel grid
        #logging.info("set pallet")
        start_time = time.time()
        self.paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE))
        #logging.info("set pallet: %0.2f seconds" % (time.time() - start_time))

    def _set_rotation(self):
        #logging.info("set rotation")
        start_time = time.time()
        self.paper.send(
            SetCurrentDisplayRotation(SetCurrentDisplayRotation.NORMAL))
        #logging.info("set rotation: %0.2f seconds" % (
        #   time.time() - start_time))

    def _set_font_size_small(self):
        #logging.info("set font size")
        start_time = time.time()
        self.paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        #logging.info("set font size: %0.2f seconds" % (
        #   time.time() - start_time))

    def _set_font_size_medium(self):
        #logging.info("set font size")
        start_time = time.time()
        self.paper.send(SetEnFontSize(SetEnFontSize.FOURTYEIGHT))
        #logging.info("set font size: %0.2f seconds" % (
        #   time.time() - start_time))

    def _set_font_size_large(self):
        #logging.info("set font size")
        start_time = time.time()
        self.paper.send(SetEnFontSize(SetEnFontSize.SIXTYFOUR))
        #logging.info("set font size: %0.2f seconds" % (
        #   time.time() - start_time))

    def _setup_display(self):
        start_time = time.time()
        #logging.info("setup display")
        self._handshake()
        # give the display a chance to initialize
        time.sleep(2)
        # set up specific settings
        self._set_rotation()
        # make sure setup is acknowledged before proceeding into normal
        # operation
        self.paper.read_responses(timeout=10)
        #logging.info("finished setup in %0.2f seconds" % (
        #   time.time() - start_time))

    def _fill_rectangle(self, x1, y1, x2, y2):
        self.paper.send(FillRectangle(x1, y1, x2, y2))

    def _draw_qr(self, qr_draw):
        start_time = time.time()
        read_count = 0
        x_offset, y_offset, scale = qr_draw.place_inside_box(200, 0, 600)
        for color, x1, y1, x2, y2 in qr_draw.iter_draw_params(x_offset,
                                                              y_offset,
                                                              scale):
            if color == 0xff:
                continue
            else:
                self._fill_rectangle(x1, y1, x2, y2)
        #logging.info("draw qr: %0.2f seconds" % (time.time() - start_time))

    def _refresh(self):
        if self.refresh_cb:
            self.refresh_cb()
        start_time = time.time()
        self.paper.send(RefreshAndUpdate())
        #logging.info("refresh update: %0.2f seconds" % (
        #   time.time() - start_time))

    def _draw_label(self, title_lines, artist_lines, price_lines):
        start_time = time.time()
        self._set_font_size_medium()
        x = 10
        y = 80   
        for line in title_lines:
            logging.info("title line: %s" % line)
            self.paper.send(DisplayText(x, y, line.encode("gb2312")))
            y += 45

        y += 60
        self._set_font_size_small()
        for line in artist_lines:
            logging.info("artist line: %s" % line)
            self.paper.send(DisplayText(x, y, line.encode("gb2312")))
            y += 30
        y += 120
        self._set_font_size_medium()
        for line in price_lines:
            logging.info("price_line: %s" % line)
            self.paper.send(DisplayText(x+5, y, line.encode("gb2312")))
            y += 45
        #logging.info("label: %0.2f seconds" % (time.time() - start_time))

    def _clear_screen(self):
        #logging.info("clearing screen")
        self.paper.send(ClearScreen())

    def split_lines(self, string, wrap):
        lines = textwrap.wrap(string, wrap)
        padded = []
        for line in lines:
            while len(line) < (wrap - 1):
                line = " " + line + " "
            padded.append(line)
        return padded

    def draw_selection(self, selection):
        qd = QRDraw(selection['invoice'])
        title_lines = self.split_lines(selection['title'], 10)
        artist_lines = self.split_lines(selection['artist'], 14)
        price_lines = self.split_lines("%.03f satoshis" % selection['price'], 8)
        start_time = time.time()
        self._clear_screen()
        self._set_pallet_gray()
        self._draw_qr(qd)
        self._set_pallet_black()
        self._draw_label(title_lines, artist_lines, price_lines)
        self._refresh()
        #logging.info("reading after: %0.2f seconds" % (
        #             time.time() - start_time))
        self.paper.read_responses()
        #logging.info("finished: %0.2f seconds" % (time.time() - start_time))

    def draw_purchased(self, price):
        self._clear_screen()
        self._set_pallet_black()
        self._set_font_size_large()
        line1 = "Lightning struck!"
        line2 = "%.03f satoshis!" % price
        self.paper.send(DisplayText(20, 150, line1.encode("gb2312")))
        self.paper.send(DisplayText(20, 250, line2.encode("gb2312")))
        self._refresh()
        self.paper.read_responses()
