#!/usr/bin/env python
#
# In order to generate large text files to test this on run the follow command
# on a *nix system:
#
# tr -dc "A-Za-z 0-9" < /dev/urandom | fold -w 100 | head -n 2048000 > 200MB-of-junk.txt
#
# This script requires Python > 3.6
#
import chardet
import re
import sys


def tail_somewhat_reinventing_the_wheel(file):
    """
    A version of tail that pretends Python's open function isn't smart enough
    to parse the file as a text stream, so we use open's raw, unbuffered FileIO
    object, and some primitive parsing ourselves.

    This function takes a file path as an argument and prints the last 10 lines
    of the file's contents.
    """
    try:
        with open(file, "rb", buffering=0) as f:
            bytestream = f.readall()  # Get contents of file as bytestream
            # This will choke on large binary files...
            # TODO: Find a way to detect the encoding without reading in the entire bytestream
            encoding = chardet.detect(bytestream)["encoding"]
            file_string = str(bytestream, encoding)  # Cast bytestream into a string
            # Use regex libraries' split method instead of stdlib's split
            # method, so that we can handle both *nix and Windows line endings
            # in one line of code.
            lines = re.split("\\n|\\r\\n", file_string)
            total_lines = len(lines)
            if total_lines > 10:
                last_ten_lines = lines[total_lines - 10 : total_lines]
                # Since the lines aren't parsed by python, in this function we
                # need to join each list item with a newline character when
                # printing.
                print(("\n").join(last_ten_lines), end="")
            else:
                print(("\n").join(lines), end="")
    except OSError as exc:
        print(f"OS error opening {file}. Do you have the correct permissions?\n{exc}")
    except IOError as exc:
        print(f"IO error opening {file}. Perhaps this file has been corrupted..\n{exc}")
    except Exception as exc:
        print(f"Unknown exception processing {file}.\n{exc}")


def tail_using_all_python_batteries(file):
    """
    A version of tail that uses the build in text parsing ability of Python's
    open function and the TextIOWrapper file object that it returns.

    This function takes a file path as an argument and prints the last 10 lines
    of the file's contents.
    """
    try:
        with open(file, "r") as f:
            # Returns an array of the file string split on newline characters.
            lines = f.readlines()
            total_lines = len(lines)
            # Slice the array of lines if it has more than 10 elements.
            if total_lines > 10:
                last_ten_lines = lines[total_lines - 10 : total_lines]
                print(("").join(last_ten_lines), end="")
            else:
                print(("").join(lines), end="")
    except UnicodeDecodeError as exc:
        # Python 3 will use unicode when converting files into the
        # TextIOWrapper file object, so will choke on binary files.
        print(f"Error decoding {file}. Cannot be parsed as a text stream.\n{exc}")
    except OSError as exc:
        print(f"OS error opening {file}. Do you have the correct permissions?\n{exc}")
    except IOError as exc:
        print(f"IO error opening {file}. Perhaps this file has been corrupted..\n{exc}")
    except Exception as exc:
        print(f"Unknown exception processing {file}.\n{exc}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # tail_somewhat_reinventing_the_wheel(sys.argv[1])
        tail_using_all_python_batteries(sys.argv[1])
    else:
        print("Please provide a file path as an argument.")
