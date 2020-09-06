import argparse
import curses
from typing import Optional
from typing import Sequence

from .window import Window


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args(argv)

    return curses.wrapper(c_main, args.filename)


def c_main(stdscr: "curses._CursesWindow", filename: str) -> int:
    with open(filename) as f:
        lines = f.read().split("\n")

    win = Window(lines, curses.COLS, curses.LINES)

    while True:
        # Update screen
        for y, line in enumerate(lines[: curses.LINES]):
            stdscr.addstr(y, 0, line)
        cx, cy = win.screen_cursor()
        stdscr.move(cy, cx)

        # Handle keypresses
        c = stdscr.getkey()
        if c == "q":
            break
        elif c == "k":
            win.up()
        elif c == "j":
            win.down()
        elif c == "h":
            win.left()
        elif c == "l":
            win.right()
        elif c == "0":
            win.home()
        elif c == "$":
            win.end()

    return 0
