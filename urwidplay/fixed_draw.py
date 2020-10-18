# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from urwid.font import Font
from urwid.font import add_font

class FreeDrawFont(Font):
    height = 15
    data = [u"""
BBBBBBBBBBBBBBBB

     ██  ██
 ███████████▄
   ███████████▄
   ███    ▀████
   ███      ███
   ███    ▄███▀
   █████████▀
   ███████████▄
   ███     ▀████
   ███       ███
   ███     ▄████
   ████████████
 ████████████▀
     ██  ██
""",]

add_font("Free Draw",FreeDrawFont)
