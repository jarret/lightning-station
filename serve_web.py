# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
from twisted.web.server import Site
from twisted.web.static import File

from logger import log

PORT = 8888

class ServeWeb(object):
    def __init__(self, reactor):
        self.reactor = reactor

    def run(self):
        cwd = os.getcwd()
        index_html = os.path.join(cwd, "htdocs/")
        log(index_html)
        assert os.path.exists(index_html), "could not find %s" % index_html
        resource = File(index_html)
        factory = Site(resource)
        self.reactor.listenTCP(PORT, factory)
