import urwid
import json


COLS = 130
ROWS = 40

PALETTE = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', 'g7', '#d06'),
    ('headings', 'white,underline', 'black', 'bold,underline'),
    ('body_text', 'dark cyan', 'light gray'),
          ]


class ScreenUI(object):
    def __init__(self, reactor):
        self.loop = self._setup_loop_background(reactor)
        self._setup_foreground()
        self.info = {}

    ###########################################################################

    def _setup_loop_background(self, reactor):
        background_widget = urwid.SolidFill()
        event_loop = urwid.TwistedEventLoop(reactor=reactor)
        loop = urwid.MainLoop(background_widget, PALETTE,
                              event_loop=event_loop,
                              unhandled_input=self.exit_on_q)
        cols, rows = loop.screen.get_cols_rows()
        self._assert_terminal_size(cols, rows)
        loop.screen.set_terminal_properties(colors=256)
        loop.widget = urwid.AttrMap(background_widget, 'bg')
        return loop

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def _assert_terminal_size(self, cols, rows):
        s = "terminal size must be %dx%d, curently: %dx%d" % (
            COLS, ROWS, cols, rows)
        assert cols == COLS, s
        assert rows == ROWS, s

    def _setup_foreground(self):
        self.loop.widget.original_widget = urwid.Filler(urwid.Pile([]))
        txt = urwid.Text(('banner', u" Hello World "), align='center')
        streak = urwid.AttrMap(txt, 'headings')
        pile = self.loop.widget.base_widget
        pile.contents.append((streak, pile.options()))

    ###########################################################################

    def _update_elapsed(self, elapsed):
        txt = urwid.Text(('banner', u" %d elapsed " % elapsed), align='center')
        newstreak = urwid.AttrMap(txt, 'headings')
        pile = self.loop.widget.base_widget # .base_widget skips the decorations
        pile.contents.pop()
        pile.contents.append((newstreak, pile.options()))

    def update_info(self, new_info):
        self.info.update(new_info)
        print(json.dumps(new_info, indent=1, sort_keys=True))
        for key, val in self.info.items():
            if key == 'elapsed':
                self._update_elapsed(val)
            elif key == 'elapsed':
                pass
            else:
                pass

    ###########################################################################

    def run(self):
        self.loop.run()
