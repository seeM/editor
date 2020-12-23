import argparse
import curses
import sys
from dataclasses import dataclass, replace


def clamp(x, lower, upper):
    if x < lower:
        return lower
    if x > upper:
        return upper
    return x


@dataclass
class Cursor:
    line: int = 0
    col: int = 0

    def line_move(self, buffer, n):
        line = clamp(self.line + n, 0, len(buffer) - 1)
        return replace(self, line=line)

    def col_move(self, buffer, n):
        col = clamp(self.col + n, 0, len(buffer[self.line]) - 1)
        return replace(self, col=col)


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
        elif k == "KEY_LEFT":
            cursor = cursor.col_move(buffer, -1)
        elif k == "KEY_DOWN":
            cursor = cursor.line_move(buffer, 1)
        elif k == "KEY_UP":
            cursor = cursor.line_move(buffer, -1)
        elif k == "KEY_RIGHT":
            cursor = cursor.col_move(buffer, 1)


if __name__ == "__main__":
    curses.wrapper(main)
