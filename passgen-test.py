#!/usr/bin/env python

import unittest
from passgen import *


class MockArgs():
    def __init__(self,
                 words=False,
                 length=100,
                 no_upper=False,
                 no_lower=False,
                 no_symbols=False,
                 no_numbers=False):
        self.words = words
        self.length = length
        self.no_upper = no_upper
        self.no_lower = no_lower
        self.no_symbols = no_symbols
        self.no_numbers = no_numbers


class TestPasswords(unittest.TestCase):

    def test_lower(self):
        print("Checking lowercase password...")
        length = 25
        args = MockArgs(length=length, no_upper=True, no_symbols=True, no_numbers=True)
        password = get_password(args)
        print(f"Password = {password}")
        self.assertTrue(password.islower() and len(password) == length)

    def test_upper(self):
        print("Checking uppercase password...")
        length = 25
        args = MockArgs(length=length, no_lower=True, no_symbols=True, no_numbers=True)
        password = get_password(args)
        print(f"Password = {password}")
        self.assertTrue(password.isupper() and len(password) == length)

if __name__ == '__main__':
    unittest.main()
