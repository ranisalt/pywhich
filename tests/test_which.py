import os
import shutil
from pathlib import Path
from random import choices
from stat import S_IFREG, S_IRWXG, S_IRWXO, S_IRWXU, S_IXGRP, S_IXOTH, S_IXUSR
from string import ascii_lowercase

import pytest
from which import find_command_in_path

PERMISSION_MASK = S_IRWXU | S_IRWXG | S_IRWXO
DEFAULT_MODE = PERMISSION_MASK ^ (S_IXUSR | S_IXGRP | S_IXOTH)


@pytest.fixture(scope="function")
def tmp_file(fs):
    full_path = Path("/tmp") / "".join(choices(ascii_lowercase, k=10))

    def wrapped(mode=DEFAULT_MODE, user="root", group="root"):
        fs.create_file(full_path, st_mode=S_IFREG | (mode & PERMISSION_MASK))
        shutil.chown(full_path, user=user, group=group)
        return full_path

    return wrapped


def test_nonexecutable(fs, tmp_file):
    file = tmp_file()

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found


def test_executable_others(fs, tmp_file):
    file = tmp_file(S_IXOTH)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]


def test_executable_group(fs, tmp_file):
    file = tmp_file(S_IXGRP, group=os.getgid())

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]


def test_executable_nongroup(fs, tmp_file):
    file = tmp_file(S_IXGRP)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found


def test_executable_user(tmp_file):
    file = tmp_file(mode=S_IXUSR, user=os.getuid())

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]


def test_executable_nonuser(tmp_file):
    file = tmp_file(mode=S_IXUSR)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found
