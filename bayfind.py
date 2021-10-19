#!/usr/bin/python

import curses
import curses.panel
import requests
import sys
import urllib

class Color:
    def __init__(self):
        """
        Initialise curses color pairs. Iterate over primary 8 bit colors adding
        colors in the form foreground_background 3 times once with all 8 colors
        in the foreground and the default terminal background as the background
        once with white as the foreground and each color as background and once
        with black as the foreground and each color as the background.
        """
        curses.use_default_colors()  # https://stackoverflow.com/a/44015131
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
            curses.init_pair(i + 7, curses.COLOR_WHITE, i)
            curses.init_pair(i + 14, curses.COLOR_BLACK, i)

        self.red_black = curses.color_pair(1)
        self.green_black = curses.color_pair(2)
        self.yellow_black = curses.color_pair(3)
        self.blue_black = curses.color_pair(4)
        self.magenta_black = curses.color_pair(5)
        self.cyan_black = curses.color_pair(6)
        self.white_black = curses.color_pair(7)
        self.white_red = curses.color_pair(8)
        self.white_green = curses.color_pair(9)
        self.white_yellow = curses.color_pair(10)
        self.white_blue = curses.color_pair(11)
        self.white_magenta = curses.color_pair(12)
        self.white_cyan = curses.color_pair(13)
        self.white_white = curses.color_pair(14)
        self.black_red = curses.color_pair(15)
        self.black_green = curses.color_pair(16)
        self.black_yellow = curses.color_pair(17)
        self.black_blue = curses.color_pair(18)
        self.black_magenta = curses.color_pair(19)
        self.black_cyan = curses.color_pair(20)
        self.black_white = curses.color_pair(21)

        self.red_black_bold = curses.color_pair(1) | curses.A_BOLD
        self.green_black_bold = curses.color_pair(2) | curses.A_BOLD
        self.yellow_black_bold = curses.color_pair(3) | curses.A_BOLD
        self.blue_black_bold = curses.color_pair(4) | curses.A_BOLD
        self.magenta_black_bold = curses.color_pair(5) | curses.A_BOLD
        self.cyan_black_bold = curses.color_pair(6) | curses.A_BOLD
        self.white_black_bold = curses.color_pair(7) | curses.A_BOLD
        self.white_red_bold = curses.color_pair(8) | curses.A_BOLD
        self.white_green_bold = curses.color_pair(9) | curses.A_BOLD
        self.white_yellow_bold = curses.color_pair(10) | curses.A_BOLD
        self.white_blue_bold = curses.color_pair(11) | curses.A_BOLD
        self.white_magenta_bold = curses.color_pair(12) | curses.A_BOLD
        self.white_cyan_bold = curses.color_pair(13) | curses.A_BOLD
        self.white_white_bold = curses.color_pair(14) | curses.A_BOLD
        self.black_red_bold = curses.color_pair(15) | curses.A_BOLD
        self.black_green_bold = curses.color_pair(16) | curses.A_BOLD
        self.black_yellow_bold = curses.color_pair(17) | curses.A_BOLD
        self.black_blue_bold = curses.color_pair(18) | curses.A_BOLD
        self.black_magenta_bold = curses.color_pair(19) | curses.A_BOLD
        self.black_cyan_bold = curses.color_pair(20) | curses.A_BOLD
        self.black_white_bold = curses.color_pair(21) | curses.A_BOLD

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


def make_columns(columns, hl):
    color = Color()
    xstart = 0
    for title, items in columns.items():
        title_length = len(title)
        longest_item = len(max(items, key=len))
        width = max(title_length, longest_item) + 1
        title_win = curses.newwin(1, width, 0, xstart)
        title_win.erase()
        title_win.bkgd(' ', color.white_blue)
        title_win.addstr(0, 0, title)
        title_win.refresh()
        items_win = curses.newwin(curses.LINES, width, 1, xstart)
        items_win.erase()

        itemnum = 0

        if hl >= curses.LINES:
            items = items[(hl - curses.LINES) + 1:hl]
        else:
            items = items[:curses.LINES]

        for item in items:
            if itemnum == hl:
                items_win.addstr(itemnum, 0, item)
                items_win.chgat(itemnum, 0, color.white_magenta_bold)
            else:
                items_win.addstr(itemnum, 0, item)
            itemnum += 1

        items_win.refresh()
        xstart += width

def get_longest_column_length(columns):
    lengths = [len(v) for k,v in columns.items()]
    return max(lengths)

def test(stdscr):
    torrents = get_torrents()

    headings = list(set().union(*(list(d.keys()) for d in torrents)))
    columns = {}

    for title in headings:
        columns[title] = [d[title] for d in torrents if title in d]

    key_order = [ "Name", "Size", "Seeders", "Leechers"]
    columns = {k: columns[k] for k in key_order}
    longest_column_length = get_longest_column_length(columns)

    stdscr.refresh()
    curses.curs_set(0)

    hl = 0
    while True:
        make_columns(columns, hl)
        key = stdscr.getch()
        if key == ord("q"):
            break
        elif key == ord("j"):
            if hl < longest_column_length:
                hl += 1
        elif key == ord("k"):
            if hl > 0:
                hl -= 1


if __name__ == "__main__":
    curses.wrapper(test)
