# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Apr-2021
# Python 3.7
# Windows 10
"""Command line manager."""

import argparse
import sys

from errors import EmptyStringException
from stringmatcher import StringMatcher


def configure_parser():
    """Argument structure configuration for command line."""
    parser = argparse.ArgumentParser(description="String search tool."
                                                 " What are you looking for?",
                                     epilog="Your logfile"
                                            " stringmatcher_log.log"
                                            " may also provide some helpful"
                                            " information. Have fun!")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--text",
                       nargs=1,
                       metavar="STRING",
                       help="Search in a text.")
    group.add_argument("-f", "--file",
                       nargs=1,
                       metavar="FILE",
                       help="Search in a text file.")
    group.add_argument("-d", "--dir",
                       nargs=1,
                       metavar="DIR",
                       help="Search all txt-files in a directory.")

    parser.add_argument("--search",
                        nargs=1,
                        metavar="SEARCHSTRING",
                        help="String pattern that is to be searched.")
    parser.add_argument("--encoding",
                        nargs=1,
                        default=["utf-8"],
                        metavar="ENC",
                        help="File encoding. Defaults to utf-8.")
    parser.add_argument("-i", "--insensitive",
                        action="store_false",
                        help="If case-insensitive search is wanted.")
    parser.add_argument("--naive",
                        action="store_true",
                        help="If naive algorithm should be used instead"
                             " of default Boyer-Moore.")
    return parser


def command_line_execution(args):
    """Manages interaction between command line and StringMatcher."""
    if args.search is None:
        parser.error("Missing argument: --search SEARCHSTRING\n"
                     "Please specify the string you want to look for."
                     " You may find help with '--help'.")
    try:
        sm = StringMatcher(args.search[0], case=args.insensitive)
    except EmptyStringException:
        parser.error(sys.exc_info()[1])

    search_func = sm.naive if args.naive else sm.boyer_moore
    if args.text:
        indices = search_func(args.text[0])
        if indices:
            print(f"Found at indices: {', '.join([str(i) for i in indices])}")
        else:
            print("No occurrences found.")

    elif args.file:
        try:
            positions = sm.search_file(args.file[0], encoding=args.encoding[0],
                                       naive=args.naive)
        except (FileNotFoundError, PermissionError):
            parser.error(sys.exc_info()[1])
        print(_prettify_file_output(positions))
        if not positions:
            print("No occurrences found.")

    elif args.dir:
        try:
            locations = sm.search_dir(args.dir[0], encoding=args.encoding[0],
                                      naive=args.naive)
        except (FileNotFoundError, NotADirectoryError):
            parser.error(sys.exc_info()[1])
        for doc, positions in locations.items():
            print(f"{doc}:\n{_prettify_file_output(positions)}")
        if not locations:
            print("No occurrences found.")

    else:
        parser.error("Missing argument: '--text STRING' OR '--file FILE' OR"
                     " '--dir DIR'\n"
                     "Please choose depending on where you want to look"
                     " for the string.")


def _prettify_file_output(positions):
    """Prettifies output string in command line for lists containing
    2-tuples of line number and a list of indices.
    """
    output = ""
    for line, shifts in positions:
        output += f"line {line}: {', '.join([str(i) for i in shifts])}\n"
    return output


if __name__ == "__main__":
    parser = configure_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        command_line_execution(args)
