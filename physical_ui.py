# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import io
import time
import qrcode

from twisted.internet import threads
from twisted.internet.task import LoopingCall

from waveshare.epaper import EPaper

from invoicedisplay import InvoiceDisplay

import RPi.GPIO as GPIO

from logger import log

BUTTON_1 = 11
BUTTON_2 = 12
BUTTON_3 = 13
BUTTON_4 = 15

LED_1 = 16
LED_2 = 18
LED_3 = 19
LED_4 = 21



class PhysicalUI(object):
    """
    This the UI of the e-ink display, buttons and LEDs connected via the
    raspberry pi's GPIO.
    """
    def __init__(self, reactor, screen_ui, jukebox):
        self.reactor = reactor
        self.screen_ui = screen_ui
        self.jukebox = jukebox
        self.blink = None
        self.drawing = False
        self.curent_label = None

        self.jukebox.set_purchased_cb(self.purchased)
        self.jukebox.set_renewed_cb(self.renewed)

        self.paper = EPaper()
        self.display = InvoiceDisplay(self.paper, refresh_cb=self.refresh_cb)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(LED_1, GPIO.OUT)
        GPIO.setup(LED_2, GPIO.OUT)
        GPIO.setup(LED_3, GPIO.OUT)
        GPIO.setup(LED_4, GPIO.OUT)

        self.state = {LED_1: False,
                      LED_2: False,
                      LED_3: False,
                      LED_4: False}
        GPIO.output(LED_1, GPIO.LOW)
        GPIO.output(LED_2, GPIO.LOW)
        GPIO.output(LED_3, GPIO.LOW)
        GPIO.output(LED_4, GPIO.LOW)


        GPIO.add_event_detect(BUTTON_1, GPIO.FALLING,
                              callback=self.button_catch, bouncetime=150)
        GPIO.add_event_detect(BUTTON_2, GPIO.FALLING,
                              callback=self.button_catch, bouncetime=150)
        GPIO.add_event_detect(BUTTON_3, GPIO.FALLING,
                              callback=self.button_catch, bouncetime=150)
        GPIO.add_event_detect(BUTTON_4, GPIO.FALLING,
                              callback=self.button_catch, bouncetime=150)

    def refresh_cb(self):
        self.blink.stop()
        self.leds_on()
        log("ok, refreshing")

    def leds_on(self):
        GPIO.output(LED_1, GPIO.HIGH)
        GPIO.output(LED_2, GPIO.HIGH)
        GPIO.output(LED_3, GPIO.HIGH)
        GPIO.output(LED_4, GPIO.HIGH)
        self.led_state = True

    def leds_off(self):
        GPIO.output(LED_1, GPIO.LOW)
        GPIO.output(LED_2, GPIO.LOW)
        GPIO.output(LED_3, GPIO.LOW)
        GPIO.output(LED_4, GPIO.LOW)
        self.led_state = False

    def leds_flip(self):
        if self.led_state:
            self.leds_off()
        else:
            self.leds_on()

    def button_catch(self, button):
        self.reactor.callFromThread(self.button, button)

    def draw_song(self, song):
        self.drawing = True
        self.leds_on()
        self.current_label = song['label']
        log("kicking off draw")
        selection = {'first_line':  song['title'],
                     'second_line': song['artist'],
                     'price':       song['price'],
                     'invoice':     song['bolt11']}
        self.blink = LoopingCall(self.leds_flip)
        self.blink.start(0.2, now=False)

        d = threads.deferToThread(self.display.draw_selection, selection)
        d.addCallback(self.finish_drawing)

    def button(self, button_no):
        if self.drawing:
            log("already drawing, dropping on floor")
            return

        log("got button: %s" % button_no)
        if button_no in {BUTTON_1, BUTTON_3}:
            self.draw_song(self.jukebox.browse_next_song())
        else:
            self.draw_song(self.jukebox.browse_prev_song())

    def finish_drawing(self, result):
        self.drawing = False
        self.leds_off()
        log("finished_drawing")

    def finish_drawing_purchased(self, result):
        self.finish_drawing(result)
        self.reactor.callLater(2.0, self.button, BUTTON_1)

    def purchased(self, price):
        if self.drawing:
            # TODO - figure out what to do. Queue draw events?
            log("already drawing, not drawing purchased.")
            return
        self.drawing = True
        self.leds_on()
        self.blink = LoopingCall(self.leds_flip)
        self.blink.start(0.2, now=False)
        d = threads.deferToThread(self.display.draw_purchased, price)
        d.addCallback(self.finish_drawing_purchased)

    def renewed(self, old_label, song):
        if self.drawing:
            # TODO - figure out what to do. Queue draw events?
            log("already drawing, not drawing renewed.")
            return
        if old_label != self.current_label:
            # don't have to renew stuff we aren't currently drawing
            return
        self.draw_song(song)

    def run(self):
        self.reactor.callLater(2.0, self.button, BUTTON_1)
