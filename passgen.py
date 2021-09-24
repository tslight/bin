#!/usr/bin/env python

from argparse import ArgumentParser
import random


def get_words():
    dictionary_file = "/usr/share/dict/words1"
    words = []

    try:
        with open(dictionary_file) as file:
            for line in file:
                words.append(line.rstrip())
    except FileNotFoundError:
        raise

    return words


def get_chars(args):
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = lower.upper()
    numbers = "0123456789"
    symbols = "[]{}():;*/\\.,#~`|\"''£$%^-=+?"

    all = lower + upper + numbers + symbols

    if args.no_lower:
        all = all.replace(lower, "")
    if args.no_numbers:
        all = all.replace(numbers, "")
    if args.no_symbols:
        all = all.replace(symbols, "")
    if args.no_upper:
        all = all.replace(upper, "")

    return all


def get_args():
    p = ArgumentParser(description=("generate a password"))
    p.add_argument("length", type=int, help="password length")
    p.add_argument("--no-lower", action="store_true", help="exclude uppercase")
    p.add_argument("--no-numbers", action="store_true", help="exclude numbers")
    p.add_argument("--no-symbols", action="store_true", help="exclude symbols")
    p.add_argument("--no-upper", action="store_true", help="exclude lowercase")
    p.add_argument("--words", action="store_true", help="use words")
    return p.parse_args()


def main():
    args = get_args()

    try:
        if args.words:
            words = get_words()
            password = " ".join(random.sample(words, args.length))
        else:
            chars = get_chars(args)
            password = "".join(random.sample(chars, args.length))
        print(password)
    except ValueError:
        print("You've excluded too many things!")
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
