import sys
from typing import Optional
from typing import Sequence


class Buffer:
    MAX_CX = sys.maxsize

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

    def _set_cx_after_vertical_movement(self) -> None:
        if self.cx > self._max_cx:
            # Cursor exceeded the line
            if self.cx > self._cx_hint:
                self._cx_hint = self.cx
            self.cx = max(self._max_cx, 0)
        else:
            self.cx = min(self._cx_hint, self._max_cx)

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

    def home(self) -> "Buffer":
        self.cx = self._cx_hint = 0
        return self

    def end(self) -> "Buffer":
        self._cx_hint = self.MAX_CX
        self.cx = min(self._cx_hint, self._max_cx)
        return self

    @property
    def _max_cx(self) -> int:
        return len(self._lines[self.cy]) - 1
