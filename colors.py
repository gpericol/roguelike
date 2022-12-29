import curses

# main
def main():
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    curses.start_color()
    curses.use_default_colors()

    for i in range(1, 256):
        curses.init_pair(i, i, -1)
        screen.addstr(str(i) + ' ', curses.color_pair(i))


    screen.refresh()
    screen.getch()
    curses.nocbreak()
    curses.echo()
    curses.endwin()

if __name__ == '__main__':
    main()