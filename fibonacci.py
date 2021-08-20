from argparse import ArgumentParser


def fibonacci(number):
    if number < 2:
        return number
    else:
        return fibonacci(number - 1) + fibonacci(number - 2)


def main():
    parser = ArgumentParser(
        description="Get fibonacci numbers"
    )
    parser.add_argument(
        'number',
        type=int,
        help="How many fibonacci numbers to compute."
    )
    args = parser.parse_args()
    nums = range(1, args.number + 1)
    fibs = [str(fibonacci(n)) for n in nums]
    pad = len(str(nums[len(fibs) - 1]))
    for i, f in enumerate(fibs):
        print("{:>{pad}}: {}".format(i + 1, f, pad=pad))


if __name__ == '__main__':
    main()
