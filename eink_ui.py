import os
import io
import qrcode

from twisted.internet import threads

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from logger import log

WIDTH = 300
HEIGHT = 400

FONTS = {
    'price':  'fonts/FreeSans.ttf',
}
for p in FONTS.values():
    path = os.path.abspath(p)
    assert os.path.exists(p), "no file? %s" % path


MOCK_BOLT11 = "lnbc50n1pdm373mpp50hlcjdrcm9u3qqqs4a926g63d3t5qwyndytqjjgknskuvmd9kc2sdz2d4shyapwwpujq6twwehkjcm9ypnx7u3qxys8q6tcv4k8xtpqw4ek2ujlwd68y6twvuazqg3zyqxqzjcuvzstexcj4zcz7ldtkwz8t5pdsghauyhkdqdxccx8ts3ta023xqzwgwxuvlu9eehh97d0qcu9k5a4u2glenrekp7w9sswydl4hneyjqqzkxf54"

class EinkUI(object):
    def qrcode_image(bolt11):
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(bolt11)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img.resize((WIDTH, WIDTH), Image.NEAREST)

    def add_text(img, price, line1, line2):
        draw = ImageDraw.Draw(img)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font = ImageFont.truetype(FONTS['price'], 20)
        # draw.text((x, y),"Sample Text",(r,g,b))
        price_text = "%d satoshis" % price
        draw.text((20, 10), price_text, 0x00, font=font)
        draw.text((20, 335), line1, 0x00, font=font)
        draw.text((20, 360), line2, 0x00, font=font)

    def gen_screen_bytes(bolt11, price, line1, line2):
        simg = Image.new("L", (WIDTH, HEIGHT), color=0xff)
        qimg = EinkUI.qrcode_image(bolt11)
        simg.paste(qimg, (0, 35))
        EinkUI.add_text(simg, price, line1, line2)
        l = simg.convert("L")
        data = bytes(l.getdata())
        return data

    ###########################################################################

    def _generate_thread_func(bolt11, price, line1, line2):
        return EinkUI.gen_screen_bytes(bolt11, price, line1, line2)

    def generate_bytes_defer(self, song, callback):
        d = threads.deferToThread(EinkUI._generate_thread_func,
                                  song['bolt11'], song['price'], song['title'],
                                  song['artist'])
        d.addCallback(callback)


