import os
import io
import qrcode

from twisted.internet import threads

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from logger import log

class PhysicalUI(object):
    """
    This the UI of the e-ink display, buttons and LEDs connected via the
    raspberry pi's GPIO.
    """
    def __init__(self, reactor, screen_ui, jukebox):
        self.reactor = reactor
        self.screen_ui = screen_ui
        self.jukebox = jukebox

        # gpi buttons
        # peridic calls to blink lights
        # thread to draw display
        # call-in to refresh screen with new invoice upon being paid
        # move forwards and backwards through songs.
        # jukebox.browse_next_song() & jukebox.browse_prev_song

    def run(self):
        pass
