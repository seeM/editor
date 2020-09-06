from editor.main import Buffer


def test_buffer_up():
    assert Buffer(cy=1).up().cy == 0


def test_buffer_up_at_first_line():
    assert Buffer().up().cy == 0


def test_buffer_down():
    assert Buffer(["foo", "bar"]).down().cy == 1


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
