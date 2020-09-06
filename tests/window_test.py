from editor.window import Window


def test_window_up():
    assert Window(["foo", "bar"], cy=1).up().cy == 0


def test_window_up_at_first_line():
    assert Window(["foo"]).up().cy == 0


def test_window_up_passed_shorter_line():
    # It correctly resets to a shorter and then longer line
    win = Window(["longer line", "short", "long line"], cx=8, cy=2)
    win.up()
    assert win.cx == 4
    assert win.cy == 1
    win.up()
    assert win.cx == 8
    assert win.cy == 0

    # It correctly resets to a shorter and then medium line
    win = Window(["long line", "short", "longer line"], cx=10, cy=2)
    win.up()
    assert win.cx == 4
    assert win.cy == 1
    win.up()
    assert win.cx == 8
    assert win.cy == 0

    # It correctly resets cx on empty lines
    win = Window(["", "foo"], cx=4, cy=1)
    win.up()
    assert win.cx == 0
    assert win.cy == 0

    # It correctly resets cx on lines of the same length
    win = Window(["short", "short"], cx=4, cy=1)
    win.up()
    assert win.cx == 4
    assert win.cy == 0

    # It correctly resets cx hint after horizontal movement
    win = Window(["foo", "", "bar"], cy=2)
    win.right().up().up()
    assert win.cx == 1
    assert win.cy == 0
    win.left().down().down()
    assert win.cx == 0
    assert win.cy == 2


def test_window_down():
    assert Window(["foo", "bar"]).down().cy == 1


def test_window_down_passed_shorter_line():
    # It correctly resets to a shorter and then longer line
    win = Window(["long line", "short", "longer line"], cx=8)
    win.down()
    assert win.cx == 4
    assert win.cy == 1
    win.down()
    assert win.cx == 8
    assert win.cy == 2

    # It correctly resets to a shorter and then medium line
    win = Window(["longer line", "short", "long line"], cx=10)
    win.down()
    assert win.cx == 4
    assert win.cy == 1
    win.down()
    assert win.cx == 8
    assert win.cy == 2

    # It correctly resets cx on empty lines
    win = Window(["foo", ""], cx=4)
    win.down()
    assert win.cx == 0
    assert win.cy == 1

    # It correctly resets cx on lines of the same length
    win = Window(["short", "short"], cx=4)
    win.down()
    assert win.cx == 4
    assert win.cy == 1

    # It correctly resets cx hint after horizontal movement
    win = Window(["foo", "", "bar"])
    win.right().down().down()
    assert win.cx == 1
    assert win.cy == 2
    win.left().up().up()
    assert win.cx == 0
    assert win.cy == 0


def test_window_down_at_last_line():
    assert Window(["foo"]).down().cy == 0


def test_window_left():
    assert Window(cx=1).left().cx == 0


def test_window_left_at_first_char():
    assert Window().left().cx == 0


def test_window_right():
    assert Window(["foo"]).right().cx == 1


def test_window_right_at_last_char():
    assert Window(["foo"], cx=2).right().cx == 2


def test_window_home():
    assert Window(["foo"], cx=2).home().cx == 0


def test_window_end():
    assert Window(["foo"]).end().cx == 2


def test_window_end_makes_vertical_movement_always_move_to_last_char():
    win = Window(["short", "longer line", "long line"])
    assert win.end().cx == 4
    assert win.down().cx == 10
    assert win.down().cx == 8


def test_window_screen_cursor():
    lines = ["foo", "bar", "baz"]
    window = Window(lines, bx=-1, by=-1, cx=2, cy=2)
    assert window.screen_cursor() == (1, 1)


def test_window_screen_lines_vertical_scroll():
    lines = ["foo", "bar", "baz"]
    window = Window(lines, width=3, height=3, by=-1, cx=2, cy=2)
    assert window.screen_lines() == ["bar", "baz"]


# def test_window_screen_lines_horizontal_scroll():
#     lines = ["foo", "bar", "baz"]
#     window = Window(lines, width=3, height=3, bx=-1, cx=2, cy=2)
#     assert window.screen_lines() == ["oo", "ar", "az"]
