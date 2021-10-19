#!/usr/bin/python

import curses
import curses.panel
import requests
import sys
import urllib


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


def make_columns(columns):
    xstart = 0
    for title, items in columns.items():
        title_length = len(title)
        longest_item = len(max(items, key=len))
        width = max(title_length, longest_item) + 3
        title_win = curses.newwin(3, width, 0, xstart)
        title_win.erase()
        title_win.border()
        title_win.addstr(1, 1, title)
        title_win.refresh()
        items_win = curses.newwin(curses.LINES - 3, width, 3, xstart)
        items_win.scrollok(True)
        items_win.erase()
        items_win.border()
        itemnum = 1
        for item in items:
            if itemnum < curses.LINES - 4:
                items_win.addstr(itemnum, 1, item)
                itemnum += 1
        items_win.refresh()
        xstart += width


def test(stdscr):
    torrents = get_torrents()

    headings = list(set().union(*(list(d.keys()) for d in torrents)))
    columns = {}

    for title in headings:
        columns[title] = [d[title] for d in torrents if title in d]

    key_order = [ "Name", "Size", "Seeders", "Leechers"]
    columns = {k : columns[k] for k in key_order}

    stdscr.refresh()
    curses.curs_set(0)

    make_columns(columns)
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(test)
