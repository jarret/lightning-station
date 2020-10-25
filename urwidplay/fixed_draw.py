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




class HalfBlock5x6Font(Font):
    height = 6
    data = [u"""
00000111112222233333444445555566666777778888899999  !!

▄▀▀▄  ▄█  ▄▀▀▄ ▄▀▀▄ ▄  █ █▀▀▀ ▄▀▀  ▀▀▀█ ▄▀▀▄ ▄▀▀▄   █
█  █   █    ▄▀   ▄▀ █▄▄█ █▄▄  █▄▄    ▐▌ ▀▄▄▀ ▀▄▄█   █
█  █   █  ▄▀   ▄  █    █    █ █  █   █  █  █    █   ▀
 ▀▀   ▀▀▀ ▀▀▀▀  ▀▀     ▀ ▀▀▀   ▀▀    ▀   ▀▀   ▀▀    ▀

""", u'''
"""######$$$$$$%%%%%&&&&&((()))******++++++,,,-----..////:::;;

█▐▌ █ █  ▄▀█▀▄ ▐▌▐▌ ▄▀▄   █ █   ▄ ▄    ▄              ▐▌
   ▀█▀█▀ ▀▄█▄    █  ▀▄▀  ▐▌ ▐▌ ▄▄█▄▄ ▄▄█▄▄    ▄▄▄▄    █  ▀  ▀
   ▀█▀█▀ ▄ █ █  ▐▌▄ █ ▀▄▌▐▌ ▐▌  ▄▀▄    █             ▐▌  ▀ ▄▀
    ▀ ▀   ▀▀▀   ▀ ▀  ▀▀   ▀ ▀              ▄▀      ▀ ▀

''', r"""
<<<<<=====>>>>>?????@@@@@@[[[[\\\\]]]]^^^^____```{{{{||}}}}~~~~''´´´

  ▄▀      ▀▄   ▄▀▀▄ ▄▀▀▀▄ █▀▀ ▐▌  ▀▀█ ▄▀▄     ▀▄  ▄▀ █ ▀▄   ▄  █ ▄▀
▄▀   ▀▀▀▀   ▀▄   ▄▀ █ █▀█ █    █    █            ▄▀  █  ▀▄ ▐▐▌▌
 ▀▄  ▀▀▀▀  ▄▀    ▀  █ ▀▀▀ █    ▐▌   █             █  █  █    ▀
   ▀      ▀      ▀   ▀▀▀  ▀▀▀   ▀ ▀▀▀     ▀▀▀▀     ▀ ▀ ▀

""", u'''
AAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGGHHHHHIIJJJJJKKKKK

▄▀▀▄ █▀▀▄ ▄▀▀▄ █▀▀▄ █▀▀▀ █▀▀▀ ▄▀▀▄ █  █ █    █ █  █
█▄▄█ █▄▄▀ █    █  █ █▄▄  █▄▄  █    █▄▄█ █    █ █▄▀
█  █ █  █ █  ▄ █  █ █    █    █ ▀█ █  █ █ ▄  █ █ ▀▄
▀  ▀ ▀▀▀   ▀▀  ▀▀▀  ▀▀▀▀ ▀     ▀▀  ▀  ▀ ▀  ▀▀  ▀  ▀

''', u'''
LLLLLMMMMMMNNNNNOOOOOPPPPPQQQQQRRRRRSSSSSTTTTT

█    █▄ ▄█ ██ █ ▄▀▀▄ █▀▀▄ ▄▀▀▄ █▀▀▄ ▄▀▀▄ ▀▀█▀▀
█    █ ▀ █ █▐▌█ █  █ █▄▄▀ █  █ █▄▄▀ ▀▄▄    █
█    █   █ █ ██ █  █ █    █ ▌█ █  █ ▄  █   █
▀▀▀▀ ▀   ▀ ▀  ▀  ▀▀  ▀     ▀▀▌ ▀  ▀  ▀▀    ▀

''', u'''
UUUUUVVVVVVWWWWWWXXXXXXYYYYYYZZZZZ

█  █ █   █ █   █ █   █ █   █ ▀▀▀█
█  █ ▐▌ ▐▌ █ ▄ █  ▀▄▀   ▀▄▀   ▄▀
█  █  █ █  ▐▌█▐▌ ▄▀ ▀▄   █   █
 ▀▀    ▀    ▀ ▀  ▀   ▀   ▀   ▀▀▀▀

''', u'''
aaaaabbbbbcccccdddddeeeeeffffggggghhhhhiijjjjkkkkk

     █            █       ▄▀▀     █    ▄   ▄ █
 ▀▀▄ █▀▀▄ ▄▀▀▄ ▄▀▀█ ▄▀▀▄ ▀█▀ ▄▀▀▄ █▀▀▄ ▄   ▄ █ ▄▀
▄▀▀█ █  █ █  ▄ █  █ █▀▀   █  ▀▄▄█ █  █ █   █ █▀▄
 ▀▀▀ ▀▀▀   ▀▀   ▀▀▀  ▀▀   ▀   ▄▄▀ ▀  ▀ ▀ ▄▄▀ ▀  ▀

''', u'''
llmmmmmmnnnnnooooopppppqqqqqrrrrssssstttt

█                                     █
█ █▀▄▀▄ █▀▀▄ ▄▀▀▄ █▀▀▄ ▄▀▀█ █▀▀ ▄▀▀▀ ▀█▀
█ █ █ █ █  █ █  █ █  █ █  █ █    ▀▀▄  █
▀ ▀   ▀ ▀  ▀  ▀▀  █▀▀   ▀▀█ ▀   ▀▀▀    ▀

''', u'''
uuuuuvvvvvwwwwwwxxxxxxyyyyyzzzzz


█  █ █  █ █ ▄ █ ▀▄ ▄▀ █  █ ▀▀█▀
█  █ ▐▌▐▌ ▐▌█▐▌  ▄▀▄  ▀▄▄█ ▄▀
 ▀▀   ▀▀   ▀ ▀  ▀   ▀  ▄▄▀ ▀▀▀▀

''', u'''
~~~~~
 ▄ ▄
▀█▀▀▄
 █▄▄▀
 █  █
▀█▀█

''']
add_font("Half Block 5x6",HalfBlock5x6Font)

