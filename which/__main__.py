import itertools
import os
from pathlib import Path

from . import __description__, __prog__, __version__, find_command_in_path


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(prog=__prog__, description=__description__)
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--all", "-a", action="store_const", const=None, default=1
    )
    parser.add_argument("command", metavar="COMMAND")

    args = parser.parse_args()
    path_list = [Path(p) for p in os.get_exec_path()]

    found = itertools.islice(
        find_command_in_path(args.command, path_list), args.all
    )
    print(*found, sep="\n")
