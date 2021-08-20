import curses
import curses.textpad


class Screen(object):
    UP = -1
    DOWN = 1

    def __init__(self, items):
        """ Initialize the screen window

        Attributes
            window: A full curses screen window

            width: The width of `window`
            height: The height of `window`

            max_lines: Maximum visible line count for `result_window`
            top: Available top line position for current page (used on scrolling)
            bottom: Available bottom line position for whole pages (as length of items)
            current: Current highlighted line number (as window cursor)
            page: Total page count which being changed corresponding to result of a query (starts from 0)

            ┌--------------------------------------┐
            |1. Item                               |
            |--------------------------------------| <- top = 1
            |2. Item                               |
            |3. Item                               |
            |4./Item///////////////////////////////| <- current = 3
            |5. Item                               |
            |6. Item                               |
            |7. Item                               |
            |8. Item                               | <- max_lines = 7
            |--------------------------------------|
            |9. Item                               |
            |10. Item                              | <- bottom = 10
            |                                      |
            |                                      | <- page = 1 (0 and 1)
            └--------------------------------------┘

        Returns
            None
        """
        self.window = None

        self.width = 0
        self.height = 0

        self.init_curses()

        self.items = items

        self.max_lines = curses.LINES
        self.top = 0
        self.btm = len(self.items)
        self.curline = 0
        self.page = self.btm // self.max_lines

        self.run()

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr()
        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.curline = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()

    def input_stream(self):
        """Waiting an input and run a proper method according to type of input"""
        while True:
            self.display()

            ch = self.window.getch()
            if ch == curses.KEY_UP:
                self.up()
            elif ch == curses.KEY_DOWN:
                self.dn()
            elif ch == curses.KEY_LEFT:
                self.pgup()
            elif ch == curses.KEY_RIGHT:
                self.pgdn()
            elif ch == curses.ascii.ESC:
                break

    def up(self):
        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if self.top > 0 and self.curline == 0:
            self.top -= 1
        # Scroll up
        # current cursor position or top position is greater than 0
        elif self.top > 0 or self.curline > 0:
            self.curline -= 1

    def dn(self):
        # next cursor position after scrolling
        next_line = self.curline + 1
        # Down direction scroll overflow: next cursor position touch the max
        # lines, but absolute position of max lines could not touch the bottom
        if (next_line == self.max_lines and
                self.top + self.max_lines < self.btm):
            self.top += 1
        # Scroll down - next cursor position is above max lines, and absolute
        # position of next cursor could not touch the bottom
        elif (next_line < self.max_lines and
              self.top + next_line < self.btm):
            self.curline += 1

    def pgup(self):
        # Page up: if current page is not a first page, page up is possible top
        # position can not be negative, so if top position is going to be
        # negative, we should set it as 0
        current_page = (self.top + self.curline) / self.max_lines
        if current_page > 0:
            self.top = max(0, self.top - self.max_lines)

    def pgdn(self):
        # Page down
        # if current page is not a last page, page down is possible
        current_page = (self.top + self.curline) / self.max_lines
        if current_page < self.page:
            self.top += self.max_lines

    def display(self):
        """Display the items on window"""
        self.window.erase()
        for idx, item in enumerate(self.items[self.top:self.top + self.max_lines]):
            # Highlight the current cursor line
            if idx == self.curline:
                self.window.addstr(idx, 0, item, curses.color_pair(2))
            else:
                self.window.addstr(idx, 0, item, curses.color_pair(1))
        self.window.refresh()


def main():
    items = [f'{num + 1}. Item' for num in range(1000)]
    Screen(items)


if __name__ == '__main__':
    main()
