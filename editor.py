# TODO: Move horizontal scrolling out of view()...
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

    def insert(self, line, col, string):
        current = self[line]
        current = current[:col] + string + current[col:]
        lines = self[:line] + [current] + self[line + 1:]
        return replace(self, lines=lines)

    def split(self, line, col):
        current = self[line]
        splitted = [current[:col], current[col:]]
        lines = self[:line] + splitted + self[line + 1:]
        return replace(self, lines=lines)

    def delete(self, line, col):
        # If at the end of the buffer, do nothing.
        if line == self.last_line and col == len(self[line]):
            return self
        # If at the end of a line, join the current and next lines.
        if col == len(self[line]) and line != self.last_line:
            string = self[line] + self[line + 1]
            lines = self[:line] + [string] + self[line + 2:]
            return replace(self, lines=lines)
        # Otherwise, delete the character.
        current = self[line]
        string = current[:col] + current[col + 1:]
        lines = self[:line] + [string] + self[line + 1:]
        return replace(self, lines=lines)


@dataclass
class Cursor:
    line: object = 0
    col: object = 0
    col_hint: object = None

    def __post_init__(self):
        if self.col_hint is None:
            self.col_hint = self.col


@dataclass
class Window:
    n_lines: object
    n_cols: object
    line: object = 0
    col: object = 0

    def __getitem__(self, index):
        if index == -1:
            index = self.n_lines - 1
        return self.buffer[index - self.line]

    @property
    def last_line(self):
        return self.line + self.n_lines - 1

    def view(self, buffer, cursor, scroll_amount=3, scroll_margin=2):
        # Scroll the window along the current line.
        self.col = 0
        while cursor.col - self.col >= self.n_cols - scroll_margin:
            self.col += scroll_amount

        strings = []
        for line, string in enumerate(buffer[self.line:self.line + self.n_lines]):
            if line == cursor.line and self.col:
                string = "«" + string[self.col + 1:]
            if len(string) > self.n_cols:
                string = string[:self.n_cols - 1] + "»"
            strings.append(string)
        return strings


# def window_right(window, buffer, cursor):


def do_right(window, buffer, cursor):
    """Move the cursor right one character."""
    if cursor.col != len(buffer[cursor.line]):
        col = cursor.col + 1
        cursor = replace(cursor, col=col, col_hint=col)
    elif cursor.line != buffer.last_line:
        line = cursor.line + 1
        col = 0
        cursor = replace(cursor, line=line, col=col, col_hint=col)
    window = window_down(window, buffer, cursor)
    return window, cursor


def do_left(window, buffer, cursor):
    """Move the cursor left one character."""
    if cursor.col != 0:
        col = cursor.col - 1
        cursor = replace(cursor, col=col, col_hint=col)
    elif cursor.line != 0:
        line = cursor.line - 1
        col = len(buffer[line])
        cursor = replace(cursor, line=line, col=col, col_hint=col)
    window = window_up(window, buffer, cursor)
    return window, cursor


def window_down(window, buffer, cursor):
    if (
        cursor.line == window.last_line + 1
        and window.last_line != buffer.last_line
    ):
        return replace(window, line=window.line + 1)
    return window


def do_down(window, buffer, cursor):
    """Move the cursor to the next line."""
    if cursor.line == buffer.last_line:
        return window, cursor
    line = cursor.line + 1
    col = min(cursor.col_hint, len(buffer[line]))
    cursor = replace(cursor, line=line, col=col)
    window = window_down(window, buffer, cursor)
    return window, cursor


def window_up(window, buffer, cursor):
    if cursor.line == window.line - 1 and window.line != 0:
        return replace(window, line=window.line - 1)
    return window


def do_up(window, buffer, cursor):
    """Move the cursor to the previous line."""
    if cursor.line == 0:
        return window, cursor
    line = cursor.line - 1
    col = min(cursor.col_hint, len(buffer[line]))
    cursor = replace(cursor, line=line, col=col)
    window = window_up(window, buffer, cursor)
    return window, cursor


# nano has do_enter in text.c
def do_enter(window, buffer, cursor):
    """Split the line at the cursor."""
    buffer = buffer.split(cursor.line, cursor.col)
    window, cursor = do_right(window, buffer, cursor)
    return window, buffer, cursor


# nano has do_output in nano.c
def do_insert(window, buffer, cursor, string):
    buffer = buffer.insert(cursor.line, cursor.col, string)
    for _ in string:
        window, cursor = do_right(window, buffer, cursor)
    return window, buffer, cursor


# nano has do_deletion in cut.c
def do_delete(buffer, cursor):
    """Delete the character under the cursor."""
    return buffer.delete(cursor.line, cursor.col)


# nano has do_backspace in cut.c
def do_backspace(window, buffer, cursor):
    """Delete the previous character."""
    # If the cursor is at the start of the buffer, do nothing.
    if cursor.line == 0 and cursor.col == 0:
        return window, buffer, cursor
    # Otherwise, move the cursor left, and delete the character under the cursor.
    window, cursor = do_left(window, buffer, cursor)
    buffer = do_delete(buffer, cursor)
    return window, buffer, cursor


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        buffer = Buffer(f.read().splitlines())

    # window = Window(curses.LINES - 1, curses.COLS - 1, buffer)
    window = Window(4, 10)
    cursor = Cursor()

    while True:
        stdscr.erase()
        for line, string in enumerate(window.view(buffer, cursor)):
            stdscr.addstr(line, 0, string)
        stdscr.move(cursor.line - window.line, cursor.col - window.col)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)
        elif k == "KEY_LEFT":
            window, cursor = do_left(window, buffer, cursor)
        elif k == "KEY_DOWN":
            window, cursor = do_down(window, buffer, cursor)
        elif k == "KEY_UP":
            window, cursor = do_up(window, buffer, cursor)
        elif k == "KEY_RIGHT":
            window, cursor = do_right(window, buffer, cursor)
        elif k == "\n":
            window, buffer, cursor = do_enter(window, buffer, cursor)
        elif k in ("KEY_BACKSPACE", "\b", "\x7f"):
            window, buffer, cursor = do_backspace(window, buffer, cursor)
        elif k in ("KEY_DELETE", "\x04"):
            buffer = do_delete(buffer, cursor)
        else:
            window, buffer, cursor = do_insert(window, buffer, cursor, k)


if __name__ == "__main__":
    curses.wrapper(main)
