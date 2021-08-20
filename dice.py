import readline
from argparse import ArgumentParser
from random import randint
from re import match
from sys import exit


def roll():
    d1 = randint(1, 6)
    d2 = randint(1, 6)
    return d1 == d2


def result():
    percent = round((WON/COUNT)*100)
    print("\nYou won {} out of {} games.".format(WON, COUNT))
    print("You lost {} out of {} games.".format(LOST, COUNT))
    print("You won {}% of your games.\n".format(percent))
    print("Goodbye.")
    exit()


def get_rolls():
    rolls = input("Enter a number of rolls (q to quit): ")
    try:
        rolls = int(rolls)
        if rolls > 0:
            return int(rolls)
    except:
        if not match('^q(uit)?$', rolls.lower()):
            print("Invalid input.")
            dice(get_rolls())

    result()


def dice(rolls, prompt):
    global COUNT, WON, LOST
    for r in range(rolls):
        COUNT += 1
        if roll():
            print("You won. Whoopee.")
            WON += 1
        else:
            print("Failed again. Loser.")
            LOST += 1
    if prompt:
        dice(get_rolls(), prompt)

    result()


def main():
    parser = ArgumentParser(
        description="Roll some dice."
    )
    parser.add_argument(
        'rolls',
        nargs='?',
        type=int,
        default=10,
        help="Number of times to roll the dice."
    )
    parser.add_argument(
        '-p',
        '--prompt',
        action='store_true',
        help="Prompt to play again."
    )
    args = parser.parse_args()
    dice(args.rolls, args.prompt)


if __name__ == '__main__':
    COUNT = 0
    WON = 0
    LOST = 0
    main()
