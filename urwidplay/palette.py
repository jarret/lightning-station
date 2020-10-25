# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


LIGHT_ORANGE = "#fa0"
DARK_ORANGE = "#f60"

LIGHT_BLUE = "#0df"
DARK_BLUE = "#00d"

LIGHT_GREEN = "#ad8"
DARK_GREEN = "#060"

LIGHT_RED = "#f68"
DARK_RED = "#d00"

LIGHT_PURPLE = "#d6a"
DARK_PURPLE = "#a0f"

LIGHT_YELLOW = "#ff6"
DARK_YELLOW = "#fd0"

BLACK = "g0"
WHITE = "g100"

LIGHT_GREY = "g82"
DARK_GREY = "g19"

GREY = DARK_GREY

NEUTRAL_GREY = 'g46'

PALETTE = [
           ('background', '', '', '', NEUTRAL_GREY, NEUTRAL_GREY),

           ('major_text', '', '', '', WHITE, BLACK),


           ('orange', '', '', '', BLACK, DARK_ORANGE),
           ('light_orange', '', '', '', BLACK, LIGHT_ORANGE),
           ('progress_orange_n', '', '', '', GREY, LIGHT_ORANGE),
           ('progress_orange_c',  '', '', '', LIGHT_ORANGE, GREY),
           ('orange_minor_text', '', '', '', LIGHT_ORANGE, BLACK),

           ('blue', '', '', '', WHITE, DARK_BLUE),
           ('progress_blue_n', '', '', '', GREY, LIGHT_BLUE),
           ('progress_blue_c',  '', '', '', LIGHT_BLUE, GREY),
           ('blue_minor_text', '', '', '', LIGHT_BLUE, BLACK),

           ('green', '', '', '', WHITE, DARK_GREEN),
           ('progress_green_n', '', '', '', GREY, LIGHT_GREEN),
           ('progress_green_c',  '', '', '', LIGHT_GREEN, GREY),
           ('green_minor_text', '', '', '', LIGHT_GREEN, BLACK),

           ('red', '', '', '', WHITE, DARK_RED),
           ('progress_red_n', '', '', '', GREY, LIGHT_RED),
           ('progress_red_c',  '', '', '', LIGHT_RED, GREY),
           ('red_minor_text', '', '', '', LIGHT_RED, BLACK),

           ('purple', '', '', '', WHITE, DARK_PURPLE),
           ('progress_purple_n', '', '', '', GREY, LIGHT_PURPLE),
           ('progress_purple_c',  '', '', '', LIGHT_PURPLE, GREY),
           ('purple_minor_text', '', '', '', LIGHT_PURPLE, BLACK),

           ('yellow', '', '', '', BLACK, DARK_YELLOW),
           ('progress_yellow_n', '', '', '', GREY, LIGHT_YELLOW),
           ('progress_yellow_c',  '', '', '', LIGHT_YELLOW, GREY),
           ('yellow_minor_text', '', '', '', LIGHT_YELLOW, BLACK),

           ('grey', '', '', '', WHITE, BLACK),
           ('progress_grey_n', '', '', '', GREY, LIGHT_GREY),
           ('progress_grey_c',  '', '', '', LIGHT_GREY, GREY),
           ('grey_minor_text', '', '', '', LIGHT_GREY, BLACK),

           ('bolt', '', '', '', DARK_YELLOW, BLACK),
           ('progress_bolt_n', '', '', '', BLACK, LIGHT_GREY),
           ('progress_bolt_c',  '', '', '', LIGHT_GREY, BLACK),
           ('bolt_minor_text', '', '', '', DARK_YELLOW, BLACK),

           ('spark', '', '', '', LIGHT_BLUE, BLACK),
           ('progress_spark_n', '', '', '', BLACK, LIGHT_GREY),
           ('progress_spark_c',  '', '', '', LIGHT_GREY, BLACK),
           ('spark_minor_text', '', '', '', LIGHT_BLUE, BLACK),

           ('coke', '', '', '', LIGHT_RED, BLACK),
           ('progress_coke_n', '', '', '', LIGHT_RED, DARK_GREY),
           ('progress_coke_c',  '', '', '', DARK_GREY, LIGHT_RED),
           ('coke_minor_text', '', '', '', LIGHT_RED, BLACK),

           ('spearmint', '', '', '', LIGHT_GREEN, BLACK),
           ('progress_spearmint_n', '', '', '', LIGHT_GREEN, DARK_GREY),
           ('progress_spearmint_c',  '', '', '', DARK_GREY, LIGHT_GREEN),
           ('spearmint_minor_text', '', '', '', LIGHT_GREEN, BLACK),
          ]


ORANGE_THEME = {
    'panel':      'orange',
    'progress_n': 'progress_orange_n',
    'progress_c': 'progress_orange_c',
    'major_text': 'major_text',
    'minor_text': 'orange_minor_text',
}

BLUE_THEME = {
    'panel':      'blue',
    'progress_n': 'progress_blue_n',
    'progress_c': 'progress_blue_c',
    'major_text': 'major_text',
    'minor_text': 'blue_minor_text',
}

GREEN_THEME = {
    'panel':      'green',
    'progress_n': 'progress_green_n',
    'progress_c': 'progress_green_c',
    'major_text': 'major_text',
    'minor_text': 'green_minor_text',
}

RED_THEME = {
    'panel':      'red',
    'progress_n': 'progress_red_n',
    'progress_c': 'progress_red_c',
    'major_text': 'major_text',
    'minor_text': 'red_minor_text',
}

PURPLE_THEME = {
    'panel':      'purple',
    'progress_n': 'progress_purple_n',
    'progress_c': 'progress_purple_c',
    'major_text': 'major_text',
    'minor_text': 'purple_minor_text',
}

YELLOW_THEME = {
    'panel':      'yellow',
    'progress_n': 'progress_yellow_n',
    'progress_c': 'progress_yellow_c',
    'major_text': 'major_text',
    'minor_text': 'yellow_minor_text',
}

GREY_THEME = {
    'panel':      'grey',
    'progress_n': 'progress_grey_n',
    'progress_c': 'progress_grey_c',
    'major_text': 'major_text',
    'minor_text': 'grey_minor_text',
}

BOLT_THEME = {
    'panel':      'bolt',
    'progress_n': 'progress_bolt_n',
    'progress_c': 'progress_bolt_c',
    'major_text': 'major_text',
    'minor_text': 'bolt_minor_text',
}

SPARK_THEME = {
    'panel':      'spark',
    'progress_n': 'progress_spark_n',
    'progress_c': 'progress_spark_c',
    'major_text': 'major_text',
    'minor_text': 'spark_minor_text',
}

COKE_THEME = {
    'panel':      'coke',
    'progress_n': 'progress_coke_n',
    'progress_c': 'progress_coke_c',
    'major_text': 'major_text',
    'minor_text': 'coke_minor_text',
}

SPEARMINT_THEME = {
    'panel':      'spearmint',
    'progress_n': 'progress_spearmint_n',
    'progress_c': 'progress_spearmint_c',
    'major_text': 'major_text',
    'minor_text': 'spearmint_minor_text',
}
