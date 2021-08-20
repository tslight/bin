#!/usr/bin/env python
from sys import argv
from itertools import permutations

perms = permutations(argv[1:])
[print(",".join(i)) for i in list(perms)]
