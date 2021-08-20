#!/usr/bin/python
import curses
import json
import sys


class Tree:
    def __init__(self, data):
        self.data = data
        if isinstance(self.data, dict):
            self.name = ""
            self.kidnames = list(data.keys())
        else:
            self.kidnames = self.name = self.data
        self.kids = None
        self.expanded = False

    def pad(self, data, width):
        return data + ' ' * (width - len(data))

    def render(self, depth, width):
        return self.pad(
            '%s%s %s' % (' ' * 4 * depth, self.icon(), self.name),
            width
        )

    def children(self):
        if self.kidnames is None:
            return []
        if self.kids is None:
            self.kids = [Tree(kid) for kid in self.kidnames]
        return self.kids

    def icon(self):
        if self.expanded:
            return '[-]'
        elif self.kidnames is None:
            return '[?]'
        elif self.children():
            return '[+]'
        else:
            return '[ ]'

    def expand(self): self.expanded = True
    def collapse(self): self.expanded = False

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
            ord('g'): 0,
            ord('G'): line - 1,
            ord('j'): curidx + 1,
            ord('k'): curidx - 1,
            ord('b'): curidx - curses.LINES,
            ord('f'): curidx + curses.LINES,
            ord('l'): 'expand',
            ord('h'): 'collapse',
            ord('\n'): 'save',
            ord('q'): quit,
            27: quit,
        }[ch]
        return parse_key(curidx, key, line)
    except KeyError:
        return None, curidx


def init(stdscr):
    curses.curs_set(0)  # get rid of cursor
    stdscr.clear()
    stdscr.refresh()
    curses.nl()
    curses.noecho()
    stdscr.timeout(0)
    stdscr.nodelay(0)


def main(stdscr, data):
    init(stdscr)
    tree = Tree(data)
    tree.expand()
    curidx = 1
    action = None

    while True:
        stdscr.clear()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        line = 0
        offset = max(0, curidx - curses.LINES + 3)
        for data, depth in tree.traverse():
            if line == curidx:
                stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
                if action == 'save':
                    return data.data
                elif action:
                    getattr(data, action)()
            else:
                stdscr.attrset(curses.color_pair(0))
            if 0 <= line - offset < curses.LINES - 1:
                stdscr.addstr(line - offset, 0,
                              data.render(depth, curses.COLS))
            line += 1
        stdscr.refresh()
        ch = stdscr.getch()
        action, curidx = get_key(ch, curidx, line)
        curidx %= line


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        print(curses.wrapper(main, data))
    else:
        print("Give me some json bitch!")
