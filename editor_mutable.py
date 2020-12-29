import argparse
import curses
import sys


class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    @property
    def bottom(self):
        return len(self) - 1

    def insert(self, cursor, string):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        new = current[:col] + string + current[col:]
        self.lines.insert(row, new)

    def split(self, cursor):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row)
        self.lines.insert(row, current[:col])
        self.lines.insert(row + 1, current[col:])

    def delete(self, cursor):
        row, col = cursor.row, cursor.col
        if (row, col) < (self.bottom, len(self[row])):
            current = self.lines.pop(row)
            if col < len(self[row]):
                new = current[:col] + current[col + 1:]
                self.lines.insert(row, new)
            else:
                next = self.lines.pop(row)
                new = current + next
                self.lines.insert(row, new)


class Cursor:
    def __init__(self, row=0, col=0, col_hint=None):
        self.row = row
        self._col = col
        self._col_hint = col if col_hint is None else col_hint

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        self._col = col
        self._col_hint = col

    def up(self, buffer):
        if self.row > 0:
            self.row -= 1
            self._clamp_col(buffer)

    def down(self, buffer):
        if self.row < buffer.bottom:
            self.row += 1
            self._clamp_col(buffer)

    def left(self, buffer):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(buffer[self.row])

    def right(self, buffer):
        if self.col < len(buffer[self.row]):
            self.col += 1
        elif self.row < buffer.bottom:
            self.row += 1
            self.col = 0

    def _clamp_col(self, buffer):
        self._col = min(self._col_hint, len(buffer[self.row]))


class Window:
    def __init__(self, n_rows, n_cols, row=0, col=0):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.row = row
        self.col = col

    @property
    def bottom(self):
        return self.row + self.n_rows - 1

    def up(self, cursor):
        if cursor.row == self.row - 1 and self.row > 0:
            self.row -= 1

    def down(self, buffer, cursor):
        if cursor.row == self.bottom + 1 and self.bottom < buffer.bottom:
            self.row += 1

    def horizontal_scroll(self, cursor, left_margin, right_margin):
        col = 0
        while cursor.col - col >= self.n_cols - right_margin:
            col += self.n_cols - right_margin - left_margin - 1
        self.col = col


class Editor:
    def __init__(self, window, buffer, cursor):
        self.window = window
        self.buffer = buffer
        self.cursor = cursor

    def up(self):
        self.cursor.up(self.buffer)
        self.window.up(self.cursor)
        self.window.horizontal_scroll(self.cursor)

    def down(self):
        self.cursor.down(self.buffer)
        self.window.down(self.buffer, self.cursor)
        self.window.horizontal_scroll(self.cursor)

    def left(self):
        self.cursor.left(self.buffer)
        self.window.up(self.cursor)
        self.window.horizontal_scroll(self.cursor)

    def right(self):
        self.cursor.right(self.buffer)
        self.window.down(self.buffer, self.cursor)
        self.window.horizontal_scroll(self.cursor)

    def newline(self):
        self.buffer.split(self.cursor)
        self.right()

    def insert(self, string):
        self.buffer.insert(self.cursor, string)
        for _ in string:
            self.right()

    def delete(self):
        self.buffer.delete(self.cursor)

    def backspace(self):
        if (self.cursor.row, self.cursor.col) > (0, 0):
            self.left()
            self.buffer.delete(self.cursor)


def render(stdscr, editor):
    window, buffer, cursor = editor.window, editor.buffer, editor.cursor

    stdscr.erase()

    buffer = buffer[window.row:window.row + window.n_rows]
    for row, string in enumerate(buffer):
        if row == cursor.row - window.row and window.col > 0:
            string = "«" + string[window.col + 1:]
        if len(string) > window.n_cols:
            string = string[:window.n_cols - 1] + "»"

        stdscr.addstr(row, 0, string)

    stdscr.move(cursor.row - window.row, cursor.col - window.col)


def handle_key(stdscr, editor):
    k = stdscr.getkey()
    if k == "q":
        sys.exit(0)
    elif k == "KEY_LEFT":
        editor.left()
    elif k == "KEY_DOWN":
        editor.down()
    elif k == "KEY_UP":
        editor.up()
    elif k == "KEY_RIGHT":
        editor.right()
    elif k == "\n":
        editor.newline()
    elif k in ("KEY_BACKSPACE", "\b", "\x7f"):
        editor.backspace()
    elif k in ("KEY_DELETE", "\x04"):
        editor.delete()
    else:
        editor.insert(k)


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
        render(stdscr, editor)
        handle_key(stdscr, editor)


if __name__ == "__main__":
    curses.wrapper(main)
