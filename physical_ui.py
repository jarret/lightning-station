import os
import io
import qrcode

from twisted.internet import threads

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

        # gpi buttons
        # peridic calls to blink lights
        # thread to draw display
        # call-in to refresh screen with new invoice upon being paid
        # move forwards and backwards through songs.
        # jukebox.browse_next_song() & jukebox.browse_prev_song

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

    def screen_draw(self, abc):
        log("draw screen")
        time.sleep(1.0)

    def button_catch(self, button):
        self.reactor.callFromThread(self.button, button_no)

    def button(self, button_no)
        if self.drawing:
            print("already drawing, dropping on floor")
            return

        print("got button: %s" % button)
        self.drawing = True
        self.leds_on()
        print("kicking off draw")
        d = threads.deferToThread(self.display.draw_selection,
                                  SELECTION_MAPPING[button])
        d.addCallback(self.finish_drawing)
        self.blink = LoopingCall(self.leds_flip)
        self.blink.start(0.2, now=False)

    def finish_drawing(self, result):
        self.drawing = False
        self.leds_off()
        print("finished_drawing")

    def run(self):
        pass
