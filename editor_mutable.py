import argparse
import curses
import sys
from dataclasses import dataclass, replace


@dataclass
class Buffer:
    lines: object

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    @property
    def last_line(self):
        return len(self) - 1

    def insert(self, cursor, string):
        line, col = cursor.line, cursor.col
        current = self.lines.pop(line)
        new = current[:col] + string + current[col:]
        self.lines.insert(line, new)

    def split(self, cursor):
        line, col = cursor.line, cursor.col
        current = self.lines.pop(line)
        self.lines.insert(line, current[:col])
        self.lines.insert(line + 1, current[col:])

    def delete(self, cursor):
        line, col = cursor.line, cursor.col
        # If at the end of the buffer, do nothing.
        if line == self.last_line and col == len(self[line]):
            return
        # If at the end of a line, join the current and next lines.
        if col == len(self[line]) and line != self.last_line:
            current = self.lines.pop(line)
            next = self.lines.pop(line)
            new = current + next
            self.lines.insert(line, new)
        # Otherwise, delete the character.
        current = self.lines.pop(line)
        new = current[:col] + current[col + 1:]
        self.lines.insert(line, new)


class Cursor:
    def __init__(self, line=0, col=0, col_hint=None):
        self.line = line
        self._col = col
        self._col_hint = col if col_hint is None else col_hint

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        self._col = value
        self._col_hint = value

    def up(self, buffer):
        if self.line > 0:
            self.line -= 1
            self._clamp_col(buffer)

    def down(self, buffer):
        if self.line < buffer.last_line:
            self.line += 1
            self._clamp_col(buffer)

    def left(self, buffer):
        if self.col > 0:
            self.col -= 1
        elif self.line > 0:
            self.line -= 1
            self.col = len(buffer[self.line])

    def right(self, buffer):
        if self.col < len(buffer[self.line]):
            self.col += 1
        elif self.line < buffer.last_line:
            self.line += 1
            self.col = 0

    def _clamp_col(self, buffer):
        self._col = min(self._col_hint, len(buffer[self.line]))


@dataclass
class Window:
    n_lines: object
    n_cols: object
    line: object = 0
    col: object = 0

    @property
    def last_line(self):
        return self.line + self.n_lines - 1

    def down(self, buffer, cursor):
        if cursor.line == self.last_line + 1 and self.last_line != buffer.last_line:
            return replace(self, line=self.line + 1)
        return self

    def up(self, cursor):
        if cursor.line == self.line - 1 and self.line != 0:
            return replace(self, line=self.line - 1)
        return self

    def horizontal_scroll(self, cursor, left_margin, right_margin):
        col = 0
        while cursor.col - col >= self.n_cols - right_margin:
            col += self.n_cols - right_margin - left_margin - 1
        return replace(self, col=col)


@dataclass
class Editor:
    window: object
    buffer: object
    cursor: object

    def right(self):
        self.cursor.right(self.buffer)
        window = self.window.down(self.buffer, self.cursor)
        return replace(self, window=window)

    def left(self):
        self.cursor.left(self.buffer)
        window = self.window.up(self.cursor)
        return replace(self, window=window)

    def down(self):
        self.cursor.down(self.buffer)
        window = self.window.down(self.buffer, self.cursor)
        return replace(self, window=window)

    def up(self):
        self.cursor.up(self.buffer)
        window = self.window.up(self.cursor)
        return replace(self, window=window)

    def newline(self):
        self.buffer.split(self.cursor)
        return self.right()

    def insert(self, string):
        self.buffer.insert(self.cursor, string)
        editor = self
        for _ in string:
            editor = editor.right()
        return editor

    def delete(self):
        self.buffer.delete(self.cursor)

    def backspace(self):
        if self.cursor.line == 0 and self.cursor.col == 0:
            return
        self.left()
        self.buffer.delete(self.cursor)

    def render(self, stdscr, left_margin=5, right_margin=2):
        stdscr.erase()

        window = self.window.horizontal_scroll(self.cursor, left_margin, right_margin)

        buffer = self.buffer[window.line:window.line + window.n_lines]
        for line, string in enumerate(buffer):
            # Add arrows for horizontal scrolling.
            if line == self.cursor.line and window.col > 0:
                string = "«" + string[window.col + 1:]
            if len(string) > window.n_cols:
                string = string[:window.n_cols - 1] + "»"

            stdscr.addstr(line, 0, string)

        stdscr.move(self.cursor.line - window.line, self.cursor.col - window.col)


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        buffer = Buffer(f.read().splitlines())

    window = Window(curses.LINES - 1, curses.COLS - 1)
    cursor = Cursor()
    editor = Editor(window, buffer, cursor)

    while True:
        editor.render(stdscr)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)
        elif k == "KEY_LEFT":
            editor = editor.left()
        elif k == "KEY_DOWN":
            editor = editor.down()
        elif k == "KEY_UP":
            editor = editor.up()
        elif k == "KEY_RIGHT":
            editor = editor.right()
        elif k == "\n":
            editor = editor.newline()
        elif k in ("KEY_BACKSPACE", "\b", "\x7f"):
            editor.backspace()
        elif k in ("KEY_DELETE", "\x04"):
            editor.delete()
        else:
            editor = editor.insert(k)


if __name__ == "__main__":
    curses.wrapper(main)
