#!/usr/bin/env python

import logging
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from os.path import expanduser
from lib.py.slack import SlackClient


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-c", "--channel", default="test-channel", help="send a slack command"
    )
    parser.add_argument(
        "-g", "--get_messages", action="store_true", help="get messages from channel"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=10, help="limit number of retrieved messages"
    )
    parser.add_argument(
        "--get_list_json", help="retrieve json object for a given list resource"
    )
    parser.add_argument(
        "--list_channels", action="store_true", help="list available slack channels"
    )
    parser.add_argument(
        "--list_users", action="store_true", help="list available slack users"
    )
    parser.add_argument("-p", "--post_message", help="a message to post to slack")
    parser.add_argument("-s", "--send_command", nargs=2, help="send a slack command")
    parser.add_argument("-t", "--token", help="pass in a slack token")
    parser.add_argument("-u", "--user", default="Bot", help="send a slack command")
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")

    return parser.parse_args()


def mklog(verbosity):
    """
    Set root logging level based on number of -v's passed in at command line.
    """
    if verbosity > 1:
        loglevel = logging.DEBUG
        logformat = "%(asctime)s %(threadName)s %(levelname)s %(message)s"
    elif verbosity == 1:
        loglevel = logging.INFO
        logformat = "%(asctime)s %(levelname)s %(message)s"
    else:
        loglevel = logging.WARNING
        logformat = "%(levelname)s %(message)s"

    logging.basicConfig(
        # filename='',
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
        stream=sys.stdout,
    )


def get_token():
    logging.info(
        f"No token provided. Checking {expanduser('~')}/.slack.token instead..."
    )
    try:
        config = ConfigParser()
        config.read(f'{expanduser("~")}/.slack.token')
        token = config["slack"]["token"]
    except Exception as error:
        logging.error(
            f"Failed to retrieve token from {expanduser('~')}/.slack.token. Aborting."
        )
        sys.exit(1)

    if token:
        logging.info(f"Found {expanduser('~')}/.slack.token")
        logging.debug(f"Token: {token}")
        return token

    logging.error(
        f"Failed to retrieve token from {expanduser('~')}/.slack.token. Aborting."
    )
    sys.exit(1)


if __name__ == "__main__":
    """
    Put your Slack token in $HOME/.slack.token in this format:

    [slack]
    token = your-super-long-token-string

    Or pass it in as a command line option. It's up to you.
    """
    args = get_args()
    mklog(args.v)

    if args.token is None:
        args.token = get_token()

    slack = SlackClient(args.token, args.channel, args.user)

    if args.post_message:
        slack.post_message(args.post_message)
    elif args.get_messages:
        print("\n".join(slack.get_messages(args.limit)))
    elif args.get_list_json:
        print(slack.get_list_json(args.get_list_json))
    elif args.list_channels:
        print("\n".join(slack.channel_names))
    elif args.list_users:
        print("\n".join(slack.get_users()))
    elif args.send_command:
        slack.send_command(args.send_command)
