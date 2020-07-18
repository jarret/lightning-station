# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import logging

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

from audio_player import AudioPlayer



class LsWsServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.tally = 0
        self.screen_ui = self.server.screen_ui
        self.web_eink_ui = self.server.web_eink_ui
        self.jukebox = self.server.jukebox
        self.audio_player = AudioPlayer()

    ###########################################################################

    def onConnect(self, request):
        logging.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        logging.info("WebSocket connection open.")
        next_song = self.jukebox.browse_next_song()
        self.web_eink_ui.generate_bytes_defer(next_song,
                                              self.screen_generated_cb)

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info("Binary message received: {0} bytes".format(
                len(payload)))
            logging.info("Binary message received: %s" % payload.hex())
        else:
            logging.info("Text message received: {0}".format(
                payload.decode('utf8')))

        self.tally += 1
        self.screen_ui.update_info({"ws_tally": self.tally})
        logging.info("payload: %s" % payload)
        self.audio_player.play_sound_effect('button')

        next_song = self.jukebox.browse_next_song()
        logging.info(next_song)
        self.web_eink_ui.generate_bytes_defer(next_song,
                                              self.screen_generated_cb)

    def screen_generated_cb(self, display_bytes):
        self.sendMessage(display_bytes, True)

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))

###############################################################################

class LsWsServerFactory(WebSocketServerFactory):
    def __init__(self, ws_url, screen_ui, web_eink_ui, jukebox):
        super().__init__(ws_url)
        self.protocol = LsWsServerProtocol
        self.protocol.server = self
        self.screen_ui = screen_ui
        self.web_eink_ui = web_eink_ui
        self.jukebox = jukebox


###############################################################################

PORT = 9000

class ServeWebsocket(object):
    def __init__(self, reactor, screen_ui, web_eink_ui, jukebox):
        self.reactor = reactor
        self.screen_ui = screen_ui
        self.web_eink_ui = web_eink_ui
        self.jukebox = jukebox
        self.reactor.callLater(0.5, self.init_ws_info)

    def init_ws_info(self):
        self.screen_ui.update_info({"ws_tally": 0})

    def run(self):
        factory = LsWsServerFactory(u"ws://127.0.0.1:%d" % PORT,
                                    self.screen_ui, self.web_eink_ui,
                                    self.jukebox)
        self.reactor.listenTCP(PORT, factory)
