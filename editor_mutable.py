import argparse
import curses
import sys


def log(*args):
    msg = " ".join(str(a) for a in args)
    with open("log.txt", "a") as f:
        f.write(msg + "\n")


class Buffer:
    def __init__(self, lines):
        self.lines = lines

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
        if not (col == len(self[line]) and line == self.last_line):
            if col < len(self[line]):
                current = self.lines.pop(line)
                new = current[:col] + current[col + 1:]
                self.lines.insert(line, new)
            else:
                current = self.lines.pop(line)
                next = self.lines.pop(line)
                new = current + next
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
    def col(self, col):
        self._col = col
        self._col_hint = col

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


class Window:
    def __init__(self, n_lines, n_cols, line=0, col=0):
        self.n_lines = n_lines
        self.n_cols = n_cols
        self.line = line
        self.col = col

    @property
    def last_line(self):
        return self.line + self.n_lines - 1

    def down(self, buffer, cursor):
        if cursor.line == self.last_line + 1 and self.last_line != buffer.last_line:
            self.line += 1

    def up(self, cursor):
        if cursor.line == self.line - 1 and self.line != 0:
            self.line -= 1

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

    def right(self):
        self.cursor.right(self.buffer)
        self.window.down(self.buffer, self.cursor)

    def left(self):
        self.cursor.left(self.buffer)
        self.window.up(self.cursor)

    def down(self):
        self.cursor.down(self.buffer)
        self.window.down(self.buffer, self.cursor)

    def up(self):
        self.cursor.up(self.buffer)
        self.window.up(self.cursor)

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
        if self.cursor.line != 0 or self.cursor.col != 0:
            self.left()
            self.buffer.delete(self.cursor)

    def render(self, stdscr, left_margin=5, right_margin=2):
        window, buffer, cursor = self.window, self.buffer, self.cursor

        stdscr.erase()

        window.horizontal_scroll(cursor, left_margin, right_margin)

        buffer = buffer[window.line:window.line + window.n_lines]
        for line, string in enumerate(buffer):
            # Add arrows for horizontal scrolling.
            if line == cursor.line - window.line and window.col > 0:
                string = "«" + string[window.col + 1:]
            if len(string) > window.n_cols:
                string = string[:window.n_cols - 1] + "»"

            stdscr.addstr(line, 0, string)

        stdscr.move(cursor.line - window.line, cursor.col - window.col)


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


if __name__ == "__main__":
    curses.wrapper(main)
