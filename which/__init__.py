import os
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from pathlib import Path
from typing import Generator, List

__prog__ = "which"
__version__ = "0.1.0"
__author__ = "Ranieri Althoff"
__author_email__ = "ranisalt@gmail.com"
__description__ = "Write the full path of COMMAND(s) to standard output."


def find_command_in_path(
    name: str, path_list: List[Path]
) -> Generator[Path, None, None]:
    for path in path_list:
        full_path = path / name

        if not full_path.is_file():
            continue

        stat = full_path.stat()
        if (
            # execable by others
            (stat.st_mode & S_IXOTH)
            or
            # execable by group
            (stat.st_mode & S_IXGRP and stat.st_gid in os.getgroups())
            or
            # execable by user
            (stat.st_mode & S_IXUSR and stat.st_uid == os.getuid())
        ):
            yield full_path
