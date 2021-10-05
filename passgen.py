#!/usr/bin/env python

from argparse import ArgumentParser
import random
import string


def get_words():
    dictionary_file = "/usr/share/dict/words"
    words = []

    try:
        with open(dictionary_file) as file:
            for line in file:
                words.append(line.rstrip())
    except FileNotFoundError:
        raise

    return words


def get_chars(args):
    all = string.printable.replace(string.whitespace, "")

    if args.no_lower:
        all = all.replace(string.ascii_lowercase, "")
    if args.no_numbers:
        all = all.replace(string.digits, "")
    if args.no_symbols:
        all = all.replace(string.punctuation, "")
    if args.no_upper:
        all = all.replace(string.ascii_uppercase, "")

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


def get_password(args):
    try:
        if args.words:
            words = get_words()
            password = " ".join(random.sample(words, args.length))
        else:
            chars = get_chars(args)
            password = "".join(random.choices(chars, k=args.length))
        return password
    except IndexError:
        raise
    except ValueError:
        raise


def main():
    args = get_args()

    try:
        print(get_password(args))
    except IndexError:
        print("You've excluded too many things!")
    except ValueError:
        print("You've excluded too many things!")
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
