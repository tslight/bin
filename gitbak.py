#!/usr/bin/env python
import argparse
import logging
import os
import shutil
import sys
from tempfile import gettempdir
from datetime import datetime


def chkpath(path):
    """
    Checks if a path exists.
    """
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        msg = "{0} does not exist.".format(path)
        raise argparse.ArgumentTypeError(msg)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--gitroot",
        type=chkpath,
        nargs="?",
        default=f"{os.path.expanduser('~')}/src",
        help="path to look for git repositories in",
    )
    parser.add_argument(
        "-d",
        "--backup_dest",
        default=f"{os.path.expanduser('~')}/Dropbox/Documents/gitbak",
        help="path to leave backup archive in",
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="increase output verbosity"
    )

    return parser.parse_args()


def mklog(verbosity):
    if verbosity > 1:
        loglevel = logging.DEBUG
    elif verbosity == 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING

    logging.basicConfig(
        # filename='',
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
        stream=sys.stdout,
    )


def mkdirp(path):
    try:
        os.makedirs(path, exist_ok=True)
        logging.debug(f"{path} exists! Good to go :-)")
        return os.path.abspath(path)
    except:
        logging.critical(f"Failed to create {path}. Aborting.")
        sys.exit(1)


if __name__ == "__main__":
    args = get_args()
    mklog(args.verbosity)
    backup_dest = mkdirp(args.backup_dest)

    print(f"Backing up all git repos in {args.gitroot} to {backup_dest}...")
    logging.debug(f"GITROOT: {args.gitroot}, BACKUP_DEST: {backup_dest}")

    tmpdir = gettempdir()
    backup_name = os.path.basename(args.gitroot)
    timestamp = datetime.now().strftime("%Y-%m%d")

    mkdirp(f"{tmpdir}/{backup_name}-{timestamp}")

    repos = [root for root, dirs, files in os.walk(args.gitroot) if ".git" in dirs]
    logging.debug(f"Found the following git repos:\n" + "\n".join(repos))

    for repo in repos:
        reponame = os.path.basename(repo)
        archive = f"{tmpdir}/{backup_name}.{timestamp}/{reponame}.{timestamp}"
        try:
            shutil.make_archive(archive, "zip", repo)
            shutil.make_archive(
                archive,
                "zip",
                root_dir=f"{repo}/..",
                base_dir=f"{reponame}",
                logger=logging,
            )
            logging.info(f"Created {archive}.zip")
        except Exception as error:
            logging.error(f"Failed to create {archive}.zip: {error}")

    archive = f"{backup_dest}/{backup_name}.{timestamp}"
    try:
        shutil.make_archive(
            archive,
            "zip",
            root_dir=f"{tmpdir}",
            base_dir=f"{backup_name}.{timestamp}",
            logger=logging,
        )
        print(f"Successfully created {archive}.zip :-)")
    except Exception as error:
        logging.error(f"Failed to create {archive}.zip: {error}")
