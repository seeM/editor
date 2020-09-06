from typing import Sequence

from .buf import Buffer


class Window:
    def __init__(
        self,
        buf: Buffer,
        width: int,
        height: int,
        bx: int = 0,
        by: int = 0,
    ):
        self._buf = buf
        self.width = width
        self.height = height
        self.bx = bx
        self.by = by

    @property
    def cx(self) -> int:
        return self.bx + self._buf.cx

    @property
    def cy(self) -> int:
        return self.by + self._buf.cy

    @property
    def lines(self) -> Sequence[str]:
        return self._buf._lines[-self.by : (self.height - self.by)]
