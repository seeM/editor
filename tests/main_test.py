from editor.main import Buffer


def test_buffer_init():
    buf = Buffer()
    assert buf.cx == buf.cy == 0


def test_buffer_up():
    buf = Buffer(cy=1)
    buf.up()
    assert buf.cy == 0


def test_buffer_down():
    buf = Buffer()
    buf.down()
    assert buf.cy == 1


def test_buffer_left():
    buf = Buffer(cx=1)
    buf.left()
    assert buf.cx == 0


def test_buffer_right():
    buf = Buffer()
    buf.right()
    assert buf.cx == 1
