import argparse
import curses
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args(argv)

    return curses.wrapper(c_main, args.filename)


def c_main(stdscr: "curses._CursesWindow", filename: str) -> int:
    with open(filename) as f:
        lines = f.read().split("\n")

    SCREEN_HEIGHT = curses.LINES

    cx = cy = 0

    while True:
        # Update screen
        for y, line in enumerate(lines[:SCREEN_HEIGHT]):
            stdscr.addstr(y, 0, line)
        stdscr.move(cy, cx)

        # Handle keypresses
        c = stdscr.getkey()
        if c == "q":
            break
        elif c == "k":
            if cy > 0:
                cy -= 1
        elif c == "j":
            cy += 1
        elif c == "h":
            if cx > 0:
                cx -= 1
        elif c == "l":
            cx += 1

    return 0
