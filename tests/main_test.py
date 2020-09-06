from editor.main import Buffer


def test_buffer_up():
    assert Buffer(["foo", "bar"], cy=1).up().cy == 0


def test_buffer_up_at_first_line():
    assert Buffer(["foo"]).up().cy == 0


def test_buffer_up_passed_shorter_line():
    # It correctly resets to a shorter and then longer line
    buf = Buffer(["longer line", "short", "long line"], cx=8, cy=2)
    buf.up()
    assert buf.cx == 4
    assert buf.cy == 1
    buf.up()
    assert buf.cx == 8
    assert buf.cy == 0

    # It correctly resets to a shorter and then medium line
    buf = Buffer(["long line", "short", "longer line"], cx=10, cy=2)
    buf.up()
    assert buf.cx == 4
    assert buf.cy == 1
    buf.up()
    assert buf.cx == 8
    assert buf.cy == 0

    # It correctly resets cx on empty lines
    buf = Buffer(["", "foo"], cx=4, cy=1)
    buf.up()
    assert buf.cx == 0
    assert buf.cy == 0

    # It correctly resets cx on lines of the same length
    buf = Buffer(["short", "short"], cx=4, cy=1)
    buf.up()
    assert buf.cx == 4
    assert buf.cy == 0

    # It correctly resets cx hint after horizontal movement
    buf = Buffer(["foo", "", "bar"], cy=2)
    buf.right().up().up()
    assert buf.cx == 1
    assert buf.cy == 0
    buf.left().down().down()
    assert buf.cx == 0
    assert buf.cy == 2


def test_buffer_down():
    assert Buffer(["foo", "bar"]).down().cy == 1


def test_buffer_down_passed_shorter_line():
    # It correctly resets to a shorter and then longer line
    buf = Buffer(["long line", "short", "longer line"], cx=8)
    buf.down()
    assert buf.cx == 4
    assert buf.cy == 1
    buf.down()
    assert buf.cx == 8
    assert buf.cy == 2

    # It correctly resets to a shorter and then medium line
    buf = Buffer(["longer line", "short", "long line"], cx=10)
    buf.down()
    assert buf.cx == 4
    assert buf.cy == 1
    buf.down()
    assert buf.cx == 8
    assert buf.cy == 2

    # It correctly resets cx on empty lines
    buf = Buffer(["foo", ""], cx=4)
    buf.down()
    assert buf.cx == 0
    assert buf.cy == 1

    # It correctly resets cx on lines of the same length
    buf = Buffer(["short", "short"], cx=4)
    buf.down()
    assert buf.cx == 4
    assert buf.cy == 1

    # It correctly resets cx hint after horizontal movement
    buf = Buffer(["foo", "", "bar"])
    buf.right().down().down()
    assert buf.cx == 1
    assert buf.cy == 2
    buf.left().up().up()
    assert buf.cx == 0
    assert buf.cy == 0


def test_buffer_down_at_last_line():
    assert Buffer(["foo"]).down().cy == 0


def test_buffer_left():
    assert Buffer(cx=1).left().cx == 0


def test_buffer_left_at_first_char():
    assert Buffer().left().cx == 0


def test_buffer_right():
    assert Buffer(["foo"]).right().cx == 1


def test_buffer_right_at_last_char():
    assert Buffer(["foo"], cx=2).right().cx == 2
