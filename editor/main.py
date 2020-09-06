import argparse
import curses
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args(argv)

    return curses.wrapper(c_main, args.filename)


def c_main(stdscr: "curses._CursesWindow", filename: str) -> int:
    with open(filename) as f:
        lines = f.read().split("\n")

    SCREEN_HEIGHT = curses.LINES

    buf = Buffer(lines)

    while True:
        # Update screen
        for y, line in enumerate(lines[:SCREEN_HEIGHT]):
            stdscr.addstr(y, 0, line)
        stdscr.move(buf.cy, buf.cx)

        # Handle keypresses
        c = stdscr.getkey()
        if c == "q":
            break
        elif c == "k":
            buf.up()
        elif c == "j":
            buf.down()
        elif c == "h":
            buf.left()
        elif c == "l":
            buf.right()

    return 0


class Buffer:
    def __init__(
        self,
        lines: Optional[Sequence[str]] = None,
        cx: int = 0,
        cy: int = 0,
    ):
        self._lines = lines or []
        self.cx = cx
        self.cy = cy

        self._cx_hint = cx

    def up(self) -> "Buffer":
        if self.cy > 0:
            self.cy -= 1
            self._set_cx_after_vertical_movement()
        return self

    def down(self) -> "Buffer":
        if self.cy < len(self._lines) - 1:
            self.cy += 1
            self._set_cx_after_vertical_movement()
        return self

    def left(self) -> "Buffer":
        if self.cx > 0:
            self.cx -= 1
            self._cx_hint = self.cx
        return self

    def right(self) -> "Buffer":
        if self.cx < self._max_cx:
            self.cx += 1
            self._cx_hint = self.cx
        return self

    def _set_cx_after_vertical_movement(self) -> None:
        if self.cx > self._max_cx:
            # Cursor exceeded the line
            if self.cx > self._cx_hint:
                self._cx_hint = self.cx
            self.cx = max(self._max_cx, 0)
        else:
            self.cx = min(self._cx_hint, self._max_cx)

    @property
    def _max_cx(self) -> int:
        return len(self._lines[self.cy]) - 1
