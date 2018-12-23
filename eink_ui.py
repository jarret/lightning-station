

WIDTH = 300
HEIGHT = 400

class EinkUI(object):
    def __init__(self):
        self.display = bytearray(WIDTH * HEIGHT)
        self.set_checker_pattern()

    def _set_pixel(self, x, y, val):
        byte = (x * HEIGHT) + y
        self.display[byte] = val

    def set_checker_pattern(self):
        last = 0x00
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if last == 0x00:
                    self._set_pixel(x, y, 0xff)
                    last = 0xff
                else:
                    self._set_pixel(x, y, 0x00)
                    last = 0x00

    def get_display_bytes(self):
        return bytes(self.display)
