# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import datetime
from collections.abc import Sequence

import pytest

import fedrq.cli
from fedrq.backends.base import ChangelogEntry, RepoqueryBase
from fedrq.cli.commands.changelogs import _positive_int


def test_get_changelogs(repo_test_rq: RepoqueryBase):
    query = repo_test_rq.query()
    for package in query:
        evr = package.evr.split(".", 1)[0]
        expected = ChangelogEntry(
            text="- Dummy changelog entry",
            author=f"Maxwell G <maxwell@gtmx.me> - {evr}",
            date=datetime.date(2023, 7, 16),
        )
        entries = list(repo_test_rq.backend.get_changelogs(package))
        assert entries == [expected]


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["packagea"]),
        pytest.param(["--src", "packagea"]),
        pytest.param(["--notsrc", "packagea"]),
        pytest.param(["--entry-limit=1", "packagea"]),
    ],
)
def test_changelog_cmd(
    patch_config_dirs, args: Sequence[str], capsys: pytest.CaptureFixture
):
    fedrq.cli.main(["changelog", *args])
    expected = """\
* Sun Jul 16 2023 Maxwell G <maxwell@gtmx.me> - 1-1
- Dummy changelog entry

"""
    out, _ = capsys.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    "args, expected_error",
    [
        pytest.param(["fjsfasdfa"], "No matches for package!"),
    ],
)
def test_changelog_cmd_error_cases(
    patch_config_dirs, args: Sequence[str], expected_error: str
):
    with pytest.raises(SystemExit, match=expected_error):
        fedrq.cli.main(["changelog", *args])


def test_changelog_cmd_too_many_names(patch_config_dirs, capsys: pytest.CaptureFixture):
    with pytest.raises(SystemExit, match="^1$"):
        fedrq.cli.main(["changelog", "packagea", "packageb"])
    assert capsys.readouterr()[1] == "ERROR: More than one package name was passed!\n"


def test_changelog_positive_int_error():
    with pytest.raises(TypeError, match="--entry-limit must be positive!"):
        _positive_int(str(-5))
