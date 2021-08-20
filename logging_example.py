import argparse
import logging
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        help="increase output verbosity",
        action="store_true"
    )
    return parser.parse_args()


def mklog(verbose):
    if verbose:
        logging.basicConfig(
            # filename='',
            format='%(asctime)s %(threadName)s %(funcName)-10s %(levelname)-6s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG,
            stream=sys.stdout
        )
    else:
        logging.basicConfig(
            # filename='',
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO,
            stream=sys.stdout
        )


if __name__ == '__main__':
    args = get_args()
    mklog(args.verbose)

    logging.debug('Quick zephyrs blow, vexing daft Jim.')
    logging.info('How quickly daft jumping zebras vex.')
