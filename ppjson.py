#!/usr/bin/env python3
import json
import sys


def pplist(l, indent=0):
    for e in l:
        if isinstance(e, dict):
            ppdict(e, indent)
        elif isinstance(e, list):
            pplist(e, indent+4)
        else:
            print(' ' * indent + str(e))


def ppdict(d, indent=0):
    for key, value in d.items():
        print(' ' * indent + str(key))
        if isinstance(value, dict):
            ppdict(value, indent+4)
        elif isinstance(value, list):
            pplist(value, indent+4)
        else:
            print(' ' * (indent+4) + str(value))


with open(sys.argv[1]) as f:
    data = json.load(f)

ppdict(data)
