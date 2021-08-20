from argparse import ArgumentParser


def funsum(nums):
    if len(nums) == 1:
        return nums[0]
    else:
        return nums[0] + funsum(nums[1:])


def main():
    parser = ArgumentParser(
        description="Sum a range of numbers in a functional manner."
    )
    parser.add_argument(
        'upto',
        type=int,
        help="The largest value in the range."
    )
    args = parser.parse_args()
    nums = list(range(1, args.upto + 1))
    my_sum = funsum(nums)
    print(my_sum)


if __name__ == '__main__':
    main()
