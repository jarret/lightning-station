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

import qrcode



MOCK_BOLT11 = "lnbc50n1pdm373mpp50hlcjdrcm9u3qqqs4a926g63d3t5qwyndytqjjgknskuvmd9kc2sdz2d4shyapwwpujq6twwehkjcm9ypnx7u3qxys8q6tcv4k8xtpqw4ek2ujlwd68y6twvuazqg3zyqxqzjcuvzstexcj4zcz7ldtkwz8t5pdsghauyhkdqdxccx8ts3ta023xqzwgwxuvlu9eehh97d0qcu9k5a4u2glenrekp7w9sswydl4hneyjqqzkxf54"


class QRDraw(object):
    def __init__(self, bolt11):
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_M,
                           box_size=1, border=0)
        qr.add_data(bolt11)
        #@qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        l = img.convert("L")
        self.width, self.height = l.size
        d = l.getdata()
        self.data = bytearray(d)

    def iter_rows(self):
        for y in range(self.height):
            yield y, self.data[y * self.width:y * self.width + self.width]

    def iter_rects(self):
        for y, row in self.iter_rows():
            x_start = 0
            color = row[0]
            for x in range(len(row)):
                if row[x] == color:
                    continue
                else:
                    x_end = x
                    yield y, x_start, x_end, row[x_start:x_end]
                    x_start = x
                    color = row[x]
            x_end = len(row)
            yield y, x_start, x_end, row[x_start:x_end]

    def iter_string_rows(self):
        rows = {}
        for y, x_start, x_end, rect in self.iter_rects():
            if y not in rows.keys():
                rows[y] = []
            s = ""
            for b in rect:
                s += "1" if b == 0x00 else "."
            rows[y].append({'y':     y,
                            'start': x_start,
                            'end':   x_end,
                            'data':  rect,
                            'str':   s})
        for rects in rows.values():
            yield "".join(rect['str'] for rect in rects)

    def iter_draw_params(self, x_offset=30, y_offset=30, scale=2):
        for y, x_start, x_end, rect in self.iter_rects():
            color = rect[0]
            print("%s, y: %d xstart: %d xend: %d" % (rect, y, x_start, x_end))
            y1 = int(y * scale) + y_offset
            y2 = int((y + 1) * scale) + y_offset
            x1 = int(x_start * scale) + x_offset
            x2 = int(x_end * scale) + x_offset
            yield color, x1, y1, x2, y2

###############################################################################

def wait_for_paper(paper):
    while paper.read():
        pass

if __name__ == '__main__':
    d = QRDraw(MOCK_BOLT11)
    print('\n'.join(d.iter_string_rows()))

    with EPaper() as paper:
        paper.send(Handshake())
        wait_for_paper(paper)
        paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))

        #paper.send(DrawRectangle(10, 10, 100, 100))
        for color, x1, y1, x2, y2 in d.iter_draw_params(scale=4):
            if color == 0xff:
                continue
            else:
                #print("sending %d %d %d %d" % (x1, y1, x2, y2))
                paper.send(FillRectangle(x1, y1, x2, y2))

        print("refreshing")
        paper.send(RefreshAndUpdate())
        print("refreshed, waiting")
        wait_for_paper(paper)
        print("waited")

