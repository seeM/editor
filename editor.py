import argparse
import curses
import sys
from dataclasses import dataclass


@dataclass
class Cursor:
    line: int = 0
    col: int = 0


@dataclass
class Window:
    n_lines: int
    n_cols: int
    line: int = 0
    col: int = 0

    def trim(self, buffer):
        return [
            string[self.col : self.col + self.n_cols]
            for string in buffer[self.line : self.line + self.n_lines]
        ]


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        buffer = f.readlines()

    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()

    while True:
        stdscr.erase()
        for line, string in enumerate(window.trim(buffer)):
            stdscr.addstr(line, 0, string)
        stdscr.move(cursor.line, cursor.col)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)
