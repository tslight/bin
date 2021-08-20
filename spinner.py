#!/usr/bin/env python

# import sys
# import time


# def spinning_cursor():
#     while True:
#         for cursor in "|/-\\":
#             yield cursor


# spinner = spinning_cursor()
# for _ in range(50):
#     sys.stdout.write(next(spinner))
#     sys.stdout.flush()
#     time.sleep(0.1)
#     sys.stdout.write("\b")

import itertools, sys, time

spinner = itertools.cycle(["-", "/", "|", "\\"])

while True:
    sys.stdout.write(next(spinner))  # write the next character
    sys.stdout.flush()  # flush stdout buffer (actual character display)
    time.sleep(0.1)
    sys.stdout.write("\b")  # erase the last written char
