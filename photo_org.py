#!/usr/bin/env python
import argparse
import logging
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags


def chkpath(path):
    """
    Checks if a path exists.
    """
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        msg = "{0} does not exist.".format(path)
        raise argparse.ArgumentTypeError(msg)


def getargs():
    """
    Return a list of valid arguments. If no argument is given, default to $PWD.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path", type=chkpath, nargs="?", default=".", help="a valid path"
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


# def get_exiftags(path):
#     exiftags = {}

#     try:
#         img = Image.open(path)
#         if hasattr(img, "_getexif"):
#             exifdata = img._getexif()
#         else:
#             return

#         if exifdata and exifdata != "None":
#             for tag, value in exifdata.items():
#                 tagname = TAGS.get(tag)
#                 exiftags[tagname] = value
#         else:
#             return

#     except IOError:
#         print("IOError accessing {}".format(path))

#     return exiftags


# def get_date(path):
#     exiftags = get_exiftags(path)
#     exifdate = "DateTimeOriginal"

#     if exiftags:
#         if exifdate in exiftags:
#             date = datetime.strptime(exiftags[exifdate], "%Y:%m:%d %H:%M:%S")
#             date = datetime.strftime(date, "%Y-%m-%d_%H-%M-%S")
#             return date
#         else:
#             return "NO " + exifdate + " TAG"
#     else:
#         return "NO EXIFTAGS"


def main():
    args = getargs()
    path = os.path.abspath(args.path)

    images = []
    videos = []

    imgext = (
        "*.[jJ][pP][gG]",
        "*.[jJ][pP][eE][gG]",
        "*.[pP][nN][gG]",
        "*.[gG][iI][fF]",
    )
    vidext = (
        "*.[mM][pP][4]",
        "*.[mM][4][vV]",
        "*.[mM][oO][vV]",
    )

    for ext in imgext:
        images = images + list(Path(path).rglob(ext))

    for ext in vidext:
        videos = videos + list(Path(path).rglob(ext))

    # for img in images:
    #     date = get_date(img)
    #     print("{} = {}".format(img, date))

    # for vid in videos:
    #     # https://stackoverflow.com/a/52492906
    #     date = get_date(vid)

    for image in videos:
        img = Image.open(image)
        exif = dict(img.getexif())
        for key, val in exif.items():
            if key in ExifTags.TAGS and "DateTime" in ExifTags.TAGS[key]:
                print(f"{ExifTags.TAGS[key]}:{repr(val)}")


if __name__ == "__main__":
    main()
