import curses

class CursesManager:
    def __init__(self):
        # refactor
        # tira fuori curses  da qui
        # e metti screen condiviso su una entity
        self.screen = curses.initscr()
        self.h = curses.LINES
        self.w = curses.COLS
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)

    def __del__(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()