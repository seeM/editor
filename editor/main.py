import argparse
import curses
import sys
from typing import Any
from typing import Iterator
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
        for y, line in enumerate(self.buffer):
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
        elif c == "^A":
            self.move_beginning_of_line()
        elif c == "^E":
            self.move_end_of_line()
        elif c == "^J":
            self.newline()
        elif c == "^?":  # backspace
            self.delete_char()
        elif c == "^D":  # del
            self.delete_forward_char()
        else:
            self.add_char(c)

    def previous_line(self) -> None:
        self.cursor = self.cursor.up(self.buffer)

    def next_line(self) -> None:
        self.cursor = self.cursor.down(self.buffer)

    def backward_char(self) -> None:
        self.cursor = self.cursor.left(self.buffer)

    def forward_char(self) -> None:
        self.cursor = self.cursor.right(self.buffer)

    def delete_char(self) -> None:
        if not (self.cursor.y == 0 and self.cursor.x == 0):
            # Move the cursor with the unmodified buffer, else it ends up at the
            # end of the new, combined line.
            cursor = self.cursor.left(self.buffer)
            self.buffer = self.buffer.delete_char(self.cursor)
            self.cursor = cursor

    def delete_forward_char(self) -> None:
        if not (
            self.cursor.y == len(self.buffer) - 1
            and self.cursor.x == len(self.buffer[self.cursor.y])
        ):
            self.buffer = self.buffer.delete_forward_char(self.cursor)

    def add_char(self, c: str) -> None:
        self.buffer = self.buffer.add_char(self.cursor, c)
        self.cursor = self.cursor.right(self.buffer)

    def newline(self) -> None:
        self.buffer = self.buffer.newline(self.cursor)
        self.cursor = self.cursor.right(self.buffer)

    def move_beginning_of_line(self) -> None:
        self.cursor = self.cursor.move_beginning_of_line()

    def move_end_of_line(self) -> None:
        self.cursor = self.cursor.move_end_of_line(self.buffer)


class Cursor:
    MAX_X = sys.maxsize

    def __init__(self, x: int = 0, y: int = 0, x_hint: Optional[int] = None):
        self.x = x
        self.y = y
        self._x_hint = x if x_hint is None else x_hint

    # Primary interface

    def up(self, buffer: "Buffer") -> "Cursor":
        return self.line_move(-1, buffer)

    def down(self, buffer: "Buffer") -> "Cursor":
        return self.line_move(1, buffer)

    def left(self, buffer: "Buffer") -> "Cursor":
        if self.x == 0 and self.y > 0:
            return self.up(buffer).move_end_of_line(buffer)
        return self.column_move(-1, buffer)

    def right(self, buffer: "Buffer") -> "Cursor":
        if self.x == len(buffer[self.y]) and self.y < len(buffer):
            return self.down(buffer).move_beginning_of_line()
        return self.column_move(1, buffer)

    def move_beginning_of_line(self) -> "Cursor":
        return Cursor(0, self.y, 0)

    def move_end_of_line(self, buffer: "Buffer") -> "Cursor":
        return Cursor(len(buffer[self.y]), self.y, self.MAX_X)

    # Convenience functions

    def line_move(self, n: int, buffer: "Buffer") -> "Cursor":
        y = clamp(self.y + n, 0, len(buffer) - 1)
        x = min(self._x_hint, len(buffer[y]))
        return Cursor(x, y, self._x_hint)

    def column_move(self, n: int, buffer: "Buffer") -> "Cursor":
        x = clamp(self.x + n, 0, len(buffer[self.y]))
        return Cursor(x, self.y, x)

    # TODO: Maybeeeee... add some nice sounding verbs

    # def at_beginning_of_line(self) -> bool:
    #     return self.x == 0

    # def at_end_of_line(self, buffer: "Buffer") -> bool:
    #     return self.x == len(buffer[self.y])

    # def in_line(self, buffer: "Buffer") -> bool:
    #     return self.x >= 0 and self.x <= len(buffer[self.y])

    # at_start_of_file

    # at_end_of_file


def clamp(x: Any, lower: Any, upper: Any) -> Any:
    if x < lower:
        return lower
    if x > upper:
        return upper
    return x


class Buffer:
    def __init__(self, lines: List[str]):
        self.lines = lines

    # Helpers

    def copy(self) -> "Buffer":
        return Buffer(self.lines.copy())

    def pop(self, index: int) -> str:
        return self.lines.pop(index)

    def insert(self, index: int, line: str) -> None:
        self.lines.insert(index, line)

    def __setitem__(self, index: int, value: str) -> None:
        self.lines[index] = value

    def __getitem__(self, index: int) -> str:
        return self.lines[index]

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self) -> Iterator[str]:
        yield from self.lines

    # Primary interface

    def delete_char(self, cursor: Cursor) -> "Buffer":
        if cursor.x == 0:
            return self.join_previous_line(cursor)

        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer.insert(cursor.y, line[: cursor.x - 1] + line[cursor.x :])
        return buffer

    def join_previous_line(self, cursor: Cursor) -> "Buffer":
        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer[cursor.y - 1] += line
        return buffer

    def delete_forward_char(self, cursor: Cursor) -> "Buffer":
        if cursor.x == len(self[cursor.y]):
            return self.join_next_line(cursor)
        lines = self.lines.copy()
        line = lines.pop(cursor.y)
        line = line[: cursor.x] + line[cursor.x + 1 :]
        lines.insert(cursor.y, line)
        return Buffer(lines)

    def join_next_line(self, cursor: Cursor) -> "Buffer":
        lines = self.lines.copy()
        line = lines.pop(cursor.y)
        lines[cursor.y] += line
        return Buffer(lines)

    def add_char(self, cursor: Cursor, c: str) -> "Buffer":
        lines = self.lines.copy()
        line = lines.pop(cursor.y)
        line = line[: cursor.x] + c + line[cursor.x :]
        lines.insert(cursor.y, line)
        return Buffer(lines)

    def newline(self, cursor: Cursor) -> "Buffer":
        lines = self.lines.copy()
        line = lines.pop(cursor.y)
        lines.insert(cursor.y, line[: cursor.x])
        lines.insert(cursor.y + 1, line[cursor.x :])
        return Buffer(lines)
