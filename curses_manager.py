import curses
from constants import *

class CursesManager:
    def __init__(self):
        self.screen = curses.initscr()
        self.h = curses.LINES
        self.w = curses.COLS
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        curses.start_color()
        curses.use_default_colors()
        self.init_colors()

    def init_colors(self):
        curses.init_pair(COLOR_WHITE, 15, -1)
        curses.init_pair(COLOR_GRAY, 59, -1)
        curses.init_pair(COLOR_RED, 196, -1)
        curses.init_pair(COLOR_DARK_GRAY, 16, -1)
        curses.init_pair(COLOR_GREEN, 2, -1)
        curses.init_pair(COLOR_LIGHT_BROWN, 166, -1)
        curses.init_pair(COLOR_BROWN, 138, -1)
        curses.init_pair(COLOR_LIGHT_RED, 4, -1)

        curses.init_pair(COLOR_TOP, -1, 8)

    def __del__(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()