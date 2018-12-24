
import qrcode
import io

from PIL import Image

from logger import log

WIDTH = 300
HEIGHT = 400



MOCK_BOLT11 = "lnbc50n1pdm373mpp50hlcjdrcm9u3qqqs4a926g63d3t5qwyndytqjjgknskuvmd9kc2sdz2d4shyapwwpujq6twwehkjcm9ypnx7u3qxys8q6tcv4k8xtpqw4ek2ujlwd68y6twvuazqg3zyqxqzjcuvzstexcj4zcz7ldtkwz8t5pdsghauyhkdqdxccx8ts3ta023xqzwgwxuvlu9eehh97d0qcu9k5a4u2glenrekp7w9sswydl4hneyjqqzkxf54"

class EinkUI(object):
    def __init__(self):
        self.display = bytearray(WIDTH * HEIGHT)
        b = self.gen_qrcode_bytes()
        self.display[0:len(b)] = b

    #def _set_pixel(self, x, y, val):
    #    byte = (x * HEIGHT) + y
    #    self.display[byte] = val
#
#    def set_checker_pattern(self):
#        last = 0x00
#        for x in range(WIDTH):
#            for y in range(HEIGHT):
#                log("hello")
#                if last == 0x00:
#                    self._set_pixel(x, y, 0xff)
#                    last = 0xff
#                else:
#                    self._set_pixel(x, y, 0x00)
#                    last = 0x00
#            if last == 0x00:
#                last = 0xff
#            else:
#                last = 0x00


    def gen_qrcode_bytes(self):
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(MOCK_BOLT11)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img = img.resize((300, 300), Image.NEAREST)
        l = img.convert("L")
        data = bytearray(l.getdata())
        return data

        #imgByteArr = io.BytesIO()
        #img.save(imgByteArr, format='PNG')
        #bs = imgByteArr.getvalue()
        #log(bs)
        #return bs


    def get_display_bytes(self):
        return bytes(self.display)
