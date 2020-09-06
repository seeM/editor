import curses


def main() -> int:
    return curses.wrapper(c_main)


def c_main(stdscr: "curses._CursesWindow") -> int:
    while True:
        # Update screen
        stdscr.addstr(0, 0, "Hello world!")

        # Handle keypresses
        c = stdscr.getkey()
        if c == "q":
            break

    return 0
