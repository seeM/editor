import argparse
import curses
import sys
from dataclasses import dataclass, replace
from typing import Optional


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
    col_hint: Optional[int] = None

    def __post_init__(self):
        if self.col_hint is None:
            self.col_hint = self.col

    def line_move(self, buffer, n):
        line = clamp(self.line + n, 0, len(buffer) - 1)
        col = min(self.col_hint, len(buffer[line]) - 1)
        return replace(self, line=line, col=col)

    def col_move(self, buffer, n):
        col = clamp(self.col + n, 0, len(buffer[self.line]) - 1)
        return replace(self, col=col, col_hint=col)


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

    def line_scroll(self, buffer, cursor, margin=1):
        line = self._scroll(
            window_pos=self.line,
            window_length=self.n_lines,
            cursor_pos=cursor.line,
            buffer_length=len(buffer),
            margin=margin,
        )
        return replace(self, line=line)

    def col_scroll(self, buffer, cursor, margin=1):
        col = self._scroll(
            window_pos=self.col,
            window_length=self.n_cols,
            cursor_pos=cursor.col,
            buffer_length=len(buffer[cursor.line]),
            margin=margin,
        )
        return replace(self, col=col)

    def _scroll(self, window_pos, window_length, cursor_pos, buffer_length, margin):
        if (p := cursor_pos - margin) < window_pos:
            return max(p, 0)
        if (p := cursor_pos - window_length + margin + 1) > window_pos:
            return min(p, buffer_length - window_length)
        return window_pos

    def translate(self, cursor):
        return cursor.line - self.line, cursor.col - self.col


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
        stdscr.move(*window.translate(cursor))

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)
        elif k == "KEY_LEFT":
            cursor = cursor.col_move(buffer, -1)
            window = window.col_scroll(buffer, cursor)
        elif k == "KEY_DOWN":
            cursor = cursor.line_move(buffer, 1)
            window = window.line_scroll(buffer, cursor)
            window = window.col_scroll(buffer, cursor)
        elif k == "KEY_UP":
            cursor = cursor.line_move(buffer, -1)
            window = window.line_scroll(buffer, cursor)
            window = window.col_scroll(buffer, cursor)
        elif k == "KEY_RIGHT":
            cursor = cursor.col_move(buffer, 1)
            window = window.col_scroll(buffer, cursor)


if __name__ == "__main__":
    curses.wrapper(main)
