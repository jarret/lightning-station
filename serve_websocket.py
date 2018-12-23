import os

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

from logger import log



class LsWsServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.tally = 0
        self.screen_ui = self.server.screen_ui
        self.eink_ui = self.server.eink_ui

    ###########################################################################

    def onConnect(self, request):
        log("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        log("WebSocket connection open.")
        self.sendMessage(self.eink_ui.get_display_bytes(), True)

    def onMessage(self, payload, isBinary):
        if isBinary:
            log("Binary message received: {0} bytes".format(len(payload)))
            log("Binary message received: %s" % payload.hex())
        else:
            log("Text message received: {0}".format(payload.decode('utf8')))

        self.tally += 1
        self.screen_ui.update_info({"ws_tally": self.tally})
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        log("WebSocket connection closed: {0}".format(reason))

###############################################################################

class LsWsServerFactory(WebSocketServerFactory):
    def __init__(self, ws_url, screen_ui, eink_ui):
        super().__init__(ws_url)
        self.protocol = LsWsServerProtocol
        self.protocol.server = self
        self.screen_ui = screen_ui
        self.eink_ui = eink_ui


###############################################################################

PORT = 9000

class ServeWebsocket(object):
    def __init__(self, reactor, screen_ui, eink_ui):
        self.reactor = reactor
        self.screen_ui = screen_ui
        self.eink_ui = eink_ui
        self.reactor.callLater(0.5, self.init_ws_info)

    def init_ws_info(self):
        self.screen_ui.update_info({"ws_tally": 0})

    def run(self):
        factory = LsWsServerFactory(u"ws://127.0.0.1:%d" % PORT,
                                    self.screen_ui, self.eink_ui)
        self.reactor.listenTCP(PORT, factory)