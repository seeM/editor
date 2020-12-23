import curses
import sys


def main(stdscr):
    while True:
        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)
