import argparse
import curses
import sys
from typing import List
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args(argv)
    return curses.wrapper(c_main, args.filename)


def c_main(stdscr: "curses._CursesWindow", filename: str) -> int:
    Editor(filename).run(stdscr)
    return 0


class Editor:
    def __init__(self, filename: str):
        with open(filename) as f:
            lines = f.read().split("\n")
        self.buffer = Buffer(lines)
        self.cursor = Cursor()

    def run(self, stdscr: "curses._CursesWindow") -> None:
        while True:
            self.render(stdscr)
            self.handle_key(stdscr)

    def render(self, stdscr: "curses._CursesWindow") -> None:
        stdscr.erase()
        for y, line in enumerate(self.buffer.lines):
            stdscr.addstr(y, 0, line)
        stdscr.move(self.cursor.y, self.cursor.x)

    def handle_key(self, stdscr: "curses._CursesWindow") -> None:
        c = curses.keyname(stdscr.getch()).decode()
        if c == "^Q":
            sys.exit(0)
        elif c == "^P":
            self.previous_line()
        elif c == "^N":
            self.next_line()
        elif c == "^B":
            self.backward_char()
        elif c == "^F":
            self.forward_char()

    def previous_line(self) -> None:
        if self.cursor.y > 0:
            self.cursor = self.cursor.up().clamp(self.buffer)

    def next_line(self) -> None:
        if self.cursor.y < self.buffer.line_count() - 1:
            self.cursor = self.cursor.down().clamp(self.buffer)

    def backward_char(self) -> None:
        if self.cursor.x > 0:
            self.cursor = self.cursor.left()

    def forward_char(self) -> None:
        if self.cursor.x < self.buffer.line_length(self.cursor.y):
            self.cursor = self.cursor.right()


class Cursor:
    def __init__(self, x: int = 0, y: int = 0, x_hint: Optional[int] = None):
        self.x = x
        self.y = y
        self._x_hint = x if x_hint is None else x_hint

    def up(self) -> "Cursor":
        return Cursor(self.x, self.y - 1, self._x_hint)

    def down(self) -> "Cursor":
        return Cursor(self.x, self.y + 1, self._x_hint)

    def left(self) -> "Cursor":
        return Cursor(self.x - 1, self.y)

    def right(self) -> "Cursor":
        return Cursor(self.x + 1, self.y)

    def clamp(self, buffer: "Buffer") -> "Cursor":
        line_length = buffer.line_length(self.y)
        if self._x_hint < line_length:
            x = self._x_hint
        else:
            x = line_length
        return Cursor(x, self.y, self._x_hint)


class Buffer:
    def __init__(self, lines: List[str]):
        self.lines = lines

    def line_count(self) -> int:
        return len(self.lines)

    def line_length(self, y: int) -> int:
        return len(self.lines[y])
