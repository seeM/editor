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

    while True:
        # Update screen
        for y, line in enumerate(lines[:SCREEN_HEIGHT]):
            stdscr.addstr(y, 0, line)

        # Handle keypresses
        c = stdscr.getkey()
        if c == "q":
            break

    return 0
