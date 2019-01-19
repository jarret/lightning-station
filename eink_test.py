#!/usr/bin/env python3

from third_party.epaper import EPaper
from third_party.epaper import EPaper
from third_party.epaper import Handshake
from third_party.epaper import RefreshAndUpdate
from third_party.epaper import SetPallet
from third_party.epaper import DrawRectangle
from third_party.epaper import DrawTriangle
from third_party.epaper import FillRectangle
from third_party.epaper import FillTriangle
from third_party.epaper import DisplayText
from third_party.epaper import SetCurrentDisplayRotation

from eink.qrdraw import QRDraw

import time
import qrcode


MOCK_BOLT11 = "lnbc50n1pdm373mpp50hlcjdrcm9u3qqqs4a926g63d3t5qwyndytqjjgknskuvmd9kc2sdz2d4shyapwwpujq6twwehkjcm9ypnx7u3qxys8q6tcv4k8xtpqw4ek2ujlwd68y6twvuazqg3zyqxqzjcuvzstexcj4zcz7ldtkwz8t5pdsghauyhkdqdxccx8ts3ta023xqzwgwxuvlu9eehh97d0qcu9k5a4u2glenrekp7w9sswydl4hneyjqqzkxf54"

class Screen(object):
    def __init__(self, paper):
        self.paper = paper
        self._setup_display()

    def _handshake(self):
        h_start = time.time()
        self.paper.send(Handshake())
        print("handshake: %0.2f" % (time.time() - h_start))

    def sync(self):
        w_start = time.time()
        while self.paper.read(size=100, timeout=2):
            pass
        print("sync: %0.2f" % (time.time() - w_start))

    def _set_pallet(self):
        p_start = time.time()
        self.paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE))
        print("pallet: %0.2f" % (time.time() - p_start))

    def _set_rotation(self):
        r_start = time.time()
        self.paper.send(
            SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        print("rotation: %0.2f" % (time.time() - r_start))

    def _setup_display(self):
        self._handshake()
        self.sync()
        self._set_pallet()
        self._set_rotation()

    def draw_qr(self, draw):
        d_start = time.time()
        for color, x1, y1, x2, y2 in draw.iter_draw_params(x_offset=100,
                                                           y_offset=300,
                                                           scale=7):
            if color == 0xff:
                continue
            else:
                #print("sending %d %d %d %d" % (x1, y1, x2, y2))
                self.paper.send(FillRectangle(x1, y1, x2, y2))
                self.paper.read(size=1, timeout=1)
        print("draw qr: %0.2f" % (time.time() - d_start))

    def refresh_update(self):
        r_start = time.time()
        self.paper.send(RefreshAndUpdate())
        print("refresh update: %0.2f" % (time.time() - r_start))

    def draw_label(self, line1, line2):
        l_start = time.time()
        self.paper.send(DisplayText(10, 100, line1.encode("gb2312")))
        self.paper.send(DisplayText(10, 140, line2.encode("gb2312")))
        print("label: %0.2f" % (time.time() - l_start))


if __name__ == '__main__':
    d = QRDraw(MOCK_BOLT11)
    line1 = "Never Gonna Give You Up!"
    line2 = "Never Gonna Let You Down!"
    print('\n'.join(d.iter_string_rows()))

    with EPaper() as paper:
        s = Screen(paper)
        s.draw_qr(d)
        s.draw_label(line1, line2)
        s.refresh_update()
        s.sync()

