#!/usr/bin/env python

import curses
import requests
import urllib
import sys


class Table:
    def __init__(self, win, rows, cols, cell):
        self.win = win
        self.cols = cols
        self.rows = rows + 1
        self.cell = cell
        self.cursor = [1, 0]
        self.shown_column = 0
        self.shown_row = 0
        self.width = win.getmaxyx()[1] - 1
        self.height = win.getmaxyx()[0]
        self.spacing = 1
        self.generate_table()

    def generate_table(self):
        rows = self.rows
        self.table = []
        x = 0
        while x < rows:
            self.table.append([""] * self.cols)
            x += 1

    def cursor(self):
        return (self.cursor[0], self.cursor[1])

    def set_cell(self, row, col, value):
        row += 1
        self.table[row][col] = str(value)

    def set_word(self, val):
        if len(val) > self.cell:
            val = val[: self.cell - 4]
            val = val + ".."
        elif len(val) < self.cell:
            x = len(val)
            while x < self.cell:
                val = " " + val
                x += 1
        return val

    def print_cell(self, y, x, val, hl, length):
        if hl == True:
            self.win.addstr(y, x, (self.set_word(val))[:length], curses.A_REVERSE)
        else:
            self.win.addstr(y, x, (self.set_word(val))[:length])

    def calc_max_shown(self, length, chars):
        return (round(length / chars), length % chars)

    def set_highlight(self, y, x):
        boolRet = False
        if (self.cursor[0] == y or self.cursor[0] == -1) and (
            self.cursor[1] == x or self.cursor[1] == -1
        ):
            boolRet = True
        return boolRet

    def print_table(self):
        max_cols = self.calc_max_shown(self.width, self.cell + self.spacing)
        max_rows = self.calc_max_shown(self.height, 1)
        y = 0
        while y < max_rows[0] and y < self.rows:
            x = 0
            while x < max_cols[0] and x < self.cols:
                if y == 0:
                    self.print_cell(
                        y,
                        x * self.cell + x * self.spacing,
                        self.set_word(self.table[0][x + self.shown_column]),
                        self.set_highlight(y + self.shown_row, x + self.shown_column),
                        self.cell,
                    )
                else:
                    self.print_cell(
                        y,
                        x * self.cell + x * self.spacing,
                        self.set_word(
                            self.table[y + self.shown_row][x + self.shown_column]
                        ),
                        self.set_highlight(y + self.shown_row, x + self.shown_column),
                        self.cell,
                    )
                x += 1
            y += 1

    def cell(self):
        return self.table[cursor[0]][cursor[1]]

    def refresh(self):
        self.win.erase()
        self.print_table()
        self.win.refresh()

    def set_column_header(self, value, col):
        self.table[0][col] = str(value)

    def shift_columns_right(self):
        if self.shown_column < self.cols:
            self.shown_column += 1
        self.refresh()

    def shift_columns_left(self):
        if self.shown_column > 0:
            self.shown_column -= 1
        self.refresh()

    def shift_rows_up(self):
        if self.shown_row > 0:
            self.shown_row -= 1
        self.refresh()

    def shift_rows_down(self):
        if self.shown_row < self.rows:
            self.shown_row += 1
        self.refresh()

    def cursor_left(self):
        if self.cursor[1] > 0:
            self.cursor[1] -= 1
            if self.cursor[1] == self.shown_column - 1 and self.shown_column > 0:
                self.shown_column -= 1
        self.refresh()

    def cursor_right(self):
        max_cols = self.calc_max_shown(self.width, self.cell + self.spacing)
        if self.cursor[1] < self.cols - 1:
            self.cursor[1] += 1
            if self.cursor[1] - self.shown_column >= max_cols[0]:
                self.shown_column += 1
        self.refresh()

    def cursor_up(self):
        if self.cursor[0] > 1:
            self.cursor[0] -= 1
            if self.cursor[0] == self.shown_row - 1 and self.shown_row > 0:
                self.shown_row -= 1
            if self.cursor[0] == self.shown_row and self.shown_row > 0:
                self.shown_row -= 1
        self.refresh()

    def cursor_down(self):
        max_rows = self.calc_max_shown(self.height, 1)
        if self.cursor[0] < self.rows - 1:
            self.cursor[0] += 1
            if self.cursor[0] - self.shown_row >= max_rows[0]:
                self.shown_row += 1
        self.refresh()

    def delete_column(self, col):
        x = 0
        while x < self.rows:
            del self.table[x][col]
            x += 1
        self.cols -= 1
        self.refresh()

    def delete_row(self, row):
        row += 1
        del self.table[row]
        self.rows -= 1
        self.refresh()

    def clear_cell(self, row, col):
        row += 1
        self.table[row][col] = " "
        self.refresh()

    def clear_row(self, row):
        x = 0
        row += 1
        while x < self.cols:
            self.table[row][x] = " "
            x += 1
        self.refresh()

    def clear_column(self, col):
        x = 0
        while x < self.rows:
            self.table[x][col] = " "
            x += 1
        self.refresh()


def generate_magnet(data):
    api_trackers = "&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2850%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce"
    return f"magnet:?xt=urn:btih:{data['info_hash']}&dn={urllib.parse.quote(data['name'])}{api_trackers}"


def get_hr_size(bytes):
    "Return the given bytes as a human friendly KB, MB, GB, or TB string"
    bytes = float(bytes)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if bytes < KB:
        return "{0} {1}".format(bytes, "Bytes" if 0 == bytes > 1 else "Byte")
    elif KB <= bytes < MB:
        return "{0:.2f} KB".format(bytes / KB)
    elif MB <= bytes < GB:
        return "{0:.2f} MB".format(bytes / MB)
    elif GB <= bytes < TB:
        return "{0:.2f} GB".format(bytes / GB)
    elif TB <= bytes:
        return "{0:.2f} TB".format(bytes / TB)


def get_torrents():
    results = requests.get(f"https://apibay.org/q.php?q={sys.argv[1]}").json()
    torrents = []

    for result in results:
        torrents.append(
            {
                "Name": result["name"],
                "Size": get_hr_size(result["size"]),
                "Seeders": result["seeders"],
                "Leechers": result["leechers"],
                "Magnet": generate_magnet(result),
            }
        )

    return torrents


def main(stdscr):
    torrents = get_torrents()
    torrent_names = [torrent["Name"] for torrent in torrents]
    longest_name = max(torrent_names, key=len)
    column_names = [*torrents[0]]

    table = Table(
        win=stdscr,
        rows=len(torrents),
        cols=len(column_names),
        cell=len(longest_name),
    )

    for col in column_names:
        table.set_column_header(col, column_names.index(col))

    for torrent in torrents:
        values = [torrent[k] for k in torrent]
        for value in values:
            table.set_cell(torrents.index(torrent), values.index(value), value)

    table.delete_row(2)
    x = 0
    while x != "q":
        table.refresh()
        x = stdscr.getkey()
        if x == "h":
            table.cursor_left()
        elif x == "l":
            table.cursor_right()
        elif x == "j":
            table.cursor_down()
        elif x == "k":
            table.cursor_up()


stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.wrapper(main)
curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()
