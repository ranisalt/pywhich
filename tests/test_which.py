import os
import pathlib
import tempfile
from stat import S_IRWXG, S_IRWXO, S_IRWXU, S_IXGRP, S_IXOTH, S_IXUSR

import pytest
from which import find_command_in_path

PERMISSION_MASK = S_IRWXU | S_IRWXG | S_IRWXO
DEFAULT_MODE = PERMISSION_MASK ^ (S_IXUSR | S_IXGRP | S_IXOTH)


@pytest.fixture(scope="function")
def tmp_file(fs):
    _, full_path = tempfile.mkstemp()

    def wrapped(mode=DEFAULT_MODE, user=0, group=0):
        os.chown(full_path, user, group)
        os.chmod(full_path, mode & PERMISSION_MASK)
        return pathlib.Path(full_path)

    return wrapped


def test_nonexecutable(fs, tmp_file):
    file = tmp_file()

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found  # nosec


def test_ignore_directory(fs, tmp_path):
    found = [*find_command_in_path(tmp_path, [tmp_path])]
    assert not found  # nosec


def test_executable_others(fs, tmp_file):
    file = tmp_file(S_IXOTH)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]  # nosec


def test_executable_group(fs, tmp_file):
    file = tmp_file(S_IXGRP, group=os.getgid())

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]  # nosec


def test_executable_nongroup(fs, tmp_file):
    file = tmp_file(S_IXGRP)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found  # nosec


def test_executable_user(tmp_file):
    file = tmp_file(mode=S_IXUSR, user=os.getuid())

    found = [*find_command_in_path(file.name, [file.parent])]
    assert found == [file]  # nosec


def test_executable_nonuser(tmp_file):
    file = tmp_file(mode=S_IXUSR)

    found = [*find_command_in_path(file.name, [file.parent])]
    assert not found  # nosec
