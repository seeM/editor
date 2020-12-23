import argparse
import curses
import sys


def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        buffer = f.readlines()

    while True:
        stdscr.erase()
        for line, string in enumerate(buffer):
            stdscr.addstr(line, 0, string)

        k = stdscr.getkey()
        if k == "q":
            sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)
