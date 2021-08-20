#!/usr/bin/python
import curses
import os
import sys


def pad(data, width):
    return data + " " * (width - len(data))


class File:
    def __init__(self, name):
        self.name = name

    def render(self, depth, width):
        return pad(
            "%s%s %s" % (" " * 4 * depth, self.icon(), os.path.basename(self.name)),
            width,
        )

    def icon(self):
        return "   "

    def traverse(self):
        yield self, 0

    def expand(self):
        pass

    def collapse(self):
        pass


class Dir(File):
    def __init__(self, name):
        File.__init__(self, name)
        try:
            self.kidnames = sorted(os.listdir(name))
        except:
            self.kidnames = None  # probably permission denied
        self.kids = None
        self.expanded = False

    def children(self):
        if self.kidnames is None:
            return []
        if self.kids is None:
            self.kids = [factory(os.path.join(self.name, kid)) for kid in self.kidnames]
        return self.kids

    def icon(self):
        if self.expanded:
            return "[-]"
        elif self.kidnames is None:
            return "[?]"
        elif self.children():
            return "[+]"
        else:
            return "[ ]"

    def expand(self):
        self.expanded = True

    def collapse(self):
        self.expanded = False

    def traverse(self):
        yield self, 0
        if not self.expanded:
            return
        for child in self.children():
            for kid, depth in child.traverse():
                yield kid, depth + 1


def parse_key(curidx, key, line):
    action = None
    if isinstance(key, str):
        action = key
    elif isinstance(key, int):
        if key < 0:
            curidx = 0
        elif key >= line:
            curidx = line - 1
        else:
            curidx = key
    else:
        quit()
    return action, curidx


def get_key(ch, curidx, line):
    try:
        key = {
            ord("g"): 0,
            ord("G"): line - 1,
            ord("j"): curidx + 1,
            ord("k"): curidx - 1,
            ord("b"): curidx - curses.LINES,
            ord("f"): curidx + curses.LINES,
            ord("l"): "expand",
            ord("h"): "collapse",
            ord("\n"): "save",
            ord("q"): quit,
            27: quit,
        }[ch]
        return parse_key(curidx, key, line)
    except KeyError:
        return None, curidx


def factory(name):
    if os.path.isdir(name):
        return Dir(name)
    else:
        return File(name)


def init(stdscr):
    stdscr.erase()
    curses.nl()
    curses.noecho()
    stdscr.timeout(0)
    stdscr.nodelay(0)
    stdscr.noutrefresh()
    curses.curs_set(0)
    curses.doupdate()


def main(stdscr, path=os.getcwd()):
    init(stdscr)
    mydir = factory(os.path.abspath(path))
    mydir.expand()
    curidx = 1
    action = None

    while True:
        stdscr.erase()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        line = 0
        offset = max(0, curidx - curses.LINES + 3)
        for data, depth in mydir.traverse():
            if line == curidx:
                stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
                if action == "save":
                    return data.name
                elif action:
                    getattr(data, action)()
            else:
                stdscr.attrset(curses.color_pair(0))
            if 0 <= line - offset < curses.LINES - 1:
                stdscr.addstr(line - offset, 0, data.render(depth, curses.COLS))
            line += 1
        stdscr.noutrefresh()
        curses.doupdate()
        ch = stdscr.getch()
        action, curidx = get_key(ch, curidx, line)
        curidx %= line


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(curses.wrapper(main, sys.argv[1]))
    else:
        print(curses.wrapper(main))
