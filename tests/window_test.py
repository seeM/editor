from editor.buf import Buffer
from editor.window import Window


def test_window_cx_cy():
    buf = Buffer(["foo", "bar", "baz"], cx=2, cy=2)
    window = Window(buf, width=3, height=3, bx=-1, by=-1)
    assert window.cx == 1
    assert window.cy == 1


def test_window_lines_vertical_scroll():
    buf = Buffer(["foo", "bar", "baz"], cx=2, cy=2)
    window = Window(buf, width=3, height=3, by=-1)
    assert window.lines == ["bar", "baz"]


def test_window_lines_horizontal_scroll():
    buf = Buffer(["foo", "bar", "baz"], cx=2, cy=2)
    window = Window(buf, width=3, height=3, bx=-1)
    assert window.lines == ["ar", "az"]
