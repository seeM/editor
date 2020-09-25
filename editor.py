# TODO: is_modified and undo/redo might be buggy
# TODO: Prompt to exit anyway on modified buffer?
import argparse
import curses.ascii
import sys
from typing import Any
from typing import Iterator
from typing import List
from typing import Optional
from typing import overload
from typing import Sequence
from typing import Tuple
from typing import Union


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
        self.buffer = Buffer(lines, filename)
        self.cursor = Cursor()
        self.window = Window(curses.COLS, curses.LINES - 1)
        self.undo_stack: List[Tuple[Buffer, Cursor]] = []
        self.redo_stack: List[Tuple[Buffer, Cursor]] = []
        self.command_line = ""

    # Main

    def run(self, stdscr: "curses._CursesWindow") -> None:
        while True:
            self.render(stdscr)
            self.command_line = ""
            self.handle_key(stdscr)

    def render(self, stdscr: "curses._CursesWindow") -> None:
        stdscr.erase()
        # Window
        for y, line in enumerate(self.window.visible_lines(self.buffer)):
            stdscr.addstr(y, 0, line)
        # Status line
        stdscr.addstr(
            self.window.height - 1,
            0,
            self.window.status_line(self.buffer, self.cursor),
            curses.A_REVERSE,
        )
        # Command line
        stdscr.addstr(self.window.height, 0, self.command_line)
        # Cursor
        stdscr.move(*self.window.cursor_position(self.cursor))

    def handle_key(self, stdscr: "curses._CursesWindow") -> None:
        c = self.getkey(stdscr)

        with open("log.txt", "a") as f:
            f.write(c + "\n")

        if c == "C-q":
            self.exit()
        elif c == "C-p":
            self.previous_line()
        elif c == "C-n":
            self.next_line()
        elif c == "C-b":
            self.backward_char()
        elif c == "C-f":
            self.forward_char()
        elif c == "C-a":
            self.move_beginning_of_line()
        elif c == "C-e":
            self.move_end_of_line()
        elif c == "C-j":  # <enter>
            self.newline()
        elif c == "<backspace>":
            self.delete_char()
        elif c == "C-d":  # del
            self.delete_forward_char()
        elif c == "C-s":
            self.save_buffer()
        elif c == "C-_":  # C-/
            self.undo()
        elif c == "M-/":
            self.redo()
        else:
            self.add_char(c)

    def exit(self) -> None:
        # TODO: If any buffer has been modified, print an error message instead.
        # TODO: Add a prompt that waits for the user to press enter to continue.
        if self.buffer.is_modified:
            self.send_message(
                f'No write since last change for buffer "{self.buffer.filename}"',
            )
            return
        sys.exit(0)

    # Keyboard

    def getkey(self, stdscr: "curses._CursesWindow") -> str:
        # TODO: Make a simple Key class that knows that some keys
        #       have multiple possible chars. E.g., C-j = RET = ...
        c = stdscr.getch()

        # Meta
        if c == curses.ascii.ESC:
            stdscr.nodelay(True)
            c2 = stdscr.getch()
            stdscr.nodelay(False)
            if c2 == curses.ERR:  # no additional key pressed
                return "<escape>"
            # Ctrl + Meta
            c2_unctrl = curses.unctrl(c2).decode("ascii")
            if curses.ascii.isctrl(c2):
                c2_key = c2_unctrl[1:].lower()
                return f"C-M-{c2_key}"
            return f"M-{c2_unctrl}"

        # Ctrl
        if curses.ascii.isctrl(c):
            c_key = curses.unctrl(c).decode("ascii")[1:].lower()
            return f"C-{c_key}"

        if c == curses.ascii.DEL:
            return "<backspace>"

        # Plain char
        if curses.ascii.isprint(c):
            return curses.unctrl(c).decode("ascii")

        raise NotImplementedError(f"Unknown character key code: {c}")

    # Cursor movement

    def previous_line(self) -> None:
        self.cursor = self.cursor.up(self.buffer)
        self.window.scroll_up(self.cursor)

    def next_line(self) -> None:
        self.cursor = self.cursor.down(self.buffer)
        self.window.scroll_down(self.cursor, self.buffer)

    def backward_char(self) -> None:
        self.cursor = self.cursor.left(self.buffer)
        self.window.scroll_up(self.cursor)

    def forward_char(self) -> None:
        self.cursor = self.cursor.right(self.buffer)
        self.window.scroll_down(self.cursor, self.buffer)

    # Buffer editing

    def delete_char(self) -> None:
        if not (self.cursor.y == 0 and self.cursor.x == 0):
            self._checkpoint()
            # Move the cursor with the unmodified buffer, else it ends up at the
            # end of the new, combined line.
            cursor = self.cursor.left(self.buffer)
            self.buffer = self.buffer.delete_char(self.cursor)
            self.cursor = cursor
            self.window.scroll_up(self.cursor)

    def delete_forward_char(self) -> None:
        if not (
            self.cursor.y == len(self.buffer) - 1
            and self.cursor.x == len(self.buffer[self.cursor.y])
        ):
            self._checkpoint()
            self.buffer = self.buffer.delete_forward_char(self.cursor)

    def add_char(self, c: str) -> None:
        self._checkpoint()
        self.buffer = self.buffer.add_char(self.cursor, c)
        self.cursor = self.cursor.right(self.buffer)

    def newline(self) -> None:
        self._checkpoint()
        self.buffer = self.buffer.newline(self.cursor)
        self.cursor = self.cursor.right(self.buffer)
        self.window.scroll_down(self.cursor, self.buffer)

    def move_beginning_of_line(self) -> None:
        self.cursor = self.cursor.move_beginning_of_line()

    def move_end_of_line(self) -> None:
        self.cursor = self.cursor.move_end_of_line(self.buffer)

    # IO

    def save_buffer(self) -> None:
        # TODO: This isn't safe! We should check if the file changed externally.
        self.buffer.save()
        self.send_message(f'"{self.buffer.filename}" {len(self.buffer)}L written')

    # Undo/redo

    def _checkpoint(self) -> None:
        self.redo_stack = []
        self.undo_stack.append((self.buffer, self.cursor))

    def undo(self) -> None:
        if self.undo_stack:
            self.redo_stack.append((self.buffer, self.cursor))
            self.buffer, self.cursor = self.undo_stack.pop()
        else:
            self.send_message("Already at oldest change")

    def redo(self) -> None:
        if self.redo_stack:
            self.undo_stack.append((self.buffer, self.cursor))
            self.buffer, self.cursor = self.redo_stack.pop()
        else:
            self.send_message("Already at newest change")

    # Messages

    def send_message(self, message: str) -> None:
        self.command_line = message


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


def clamp(x: Any, lower: Any, upper: Any) -> Any:
    if x < lower:
        return lower
    if x > upper:
        return upper
    return x


class Buffer:
    def __init__(self, lines: List[str], filename: str):
        self.lines = lines
        self.filename = filename

        self.is_modified = False

    # Helpers

    def copy(self) -> "Buffer":
        return Buffer(self.lines.copy(), self.filename)

    def pop(self, index: int) -> str:
        self.is_modified = True
        return self.lines.pop(index)

    def insert(self, index: int, line: str) -> None:
        self.is_modified = True
        self.lines.insert(index, line)

    def __setitem__(self, index: int, value: str) -> None:
        self.is_modified = True
        self.lines[index] = value

    @overload
    def __getitem__(self, index: int) -> str:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[str]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
        if isinstance(index, slice):
            return self.lines[index]
        return self.lines[index]

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self) -> Iterator[str]:
        yield from self.lines

    # Primary interface - editing

    def delete_char(self, cursor: Cursor) -> "Buffer":
        if cursor.x == 0:
            return self.join_previous_line(cursor)
        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer.insert(cursor.y, line[: cursor.x - 1] + line[cursor.x :])
        return buffer

    def join_previous_line(self, cursor: Cursor) -> "Buffer":
        buffer = self.copy()
        buffer[cursor.y - 1] += buffer.pop(cursor.y)
        return buffer

    def delete_forward_char(self, cursor: Cursor) -> "Buffer":
        if cursor.x == len(self[cursor.y]):
            return self.join_next_line(cursor)
        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer.insert(cursor.y, line[: cursor.x] + line[cursor.x + 1 :])
        return buffer

    def join_next_line(self, cursor: Cursor) -> "Buffer":
        buffer = self.copy()
        buffer[cursor.y] += buffer.pop(cursor.y + 1)
        return buffer

    def add_char(self, cursor: Cursor, c: str) -> "Buffer":
        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer.insert(cursor.y, line[: cursor.x] + c + line[cursor.x :])
        return buffer

    def newline(self, cursor: Cursor) -> "Buffer":
        buffer = self.copy()
        line = buffer.pop(cursor.y)
        buffer.insert(cursor.y, line[: cursor.x])
        buffer.insert(cursor.y + 1, line[cursor.x :])
        return buffer

    # Files

    def save(self) -> None:
        with open(self.filename, "w") as f:
            f.write("\n".join(self))
        self.is_modified = False


class Window:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    @property
    def y_end(self) -> int:
        return self.y + self.height - 1  # status height

    def visible_lines(self, buffer: Buffer) -> List[str]:
        return buffer[self.y : self.y_end]

    def cursor_position(self, cursor: Cursor) -> Tuple[int, int]:
        return cursor.y - self.y, cursor.x - self.x

    def scroll_up(self, cursor: Cursor, margin: int = 1) -> None:
        if self.y > 0 and cursor.y < self.y + margin:
            self.y -= 1

    def scroll_down(self, cursor: Cursor, buffer: Buffer, margin: int = 1) -> None:
        if self.y_end < len(buffer) and cursor.y >= self.y_end - margin:
            self.y += 1

    def status_line(self, buffer: Buffer, cursor: Cursor) -> str:
        file_status = " " + buffer.filename
        if buffer.is_modified:
            file_status += " [+]"
        cursor_status = f"L: {cursor.y + 1}/{len(buffer)} C: {cursor.x + 1}" + " "
        pad_length = self.width - len(file_status) - len(cursor_status) - 1
        return file_status + " " * pad_length + cursor_status
