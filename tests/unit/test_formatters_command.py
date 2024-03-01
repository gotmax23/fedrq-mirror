# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections.abc import Callable, Collection, Sequence
from typing import Any

import pytest
from pytest_mock import MockerFixture

import fedrq.cli
from fedrq.cli.formatters import DefaultFormatters


def test_formatters_command(capsys: pytest.CaptureFixture) -> None:
    fedrq.cli.main(["formatters"])
    expected_out = """\
a
arch
attr:
buildtime
conflicts
debug_name
description
downloadsize
e
enhances
epoch
evr
files
from_repo
full_nevra
installsize
installtime
json:
license
line:
location
multiline:
na
na-requiresmatch-src:
na-requiresmatch:
name
narm:
narmsrc:
nev
nevr
nevra
nevrr
nv
obsoletes
packager
plain
plainwithrepo
provides
r
reason
recommends
release
remote_location
repoid
reponame
requires
requiresmatch-src:
requiresmatch:
rm:
rmsrc:
size
source
source+requiresmatch:
source+rm:
source_debug_name
source_name
sourcerpm
src
suggests
summary
supplements
url
v
vendor
version
"""
    out, err = capsys.readouterr()
    assert not err
    assert out == expected_out


@pytest.mark.parametrize(
    "args,formatters_kwargs,output_check",
    [
        pytest.param(
            [], {"attrs": True, "formatters": True, "special_formatters": True}, None
        ),
        pytest.param(
            ["--formatters"],
            {"attrs": False, "special_formatters": False, "formatters": True},
            None,
        ),
        pytest.param(
            ["--formatters", "--attrs"],
            {"attrs": True, "special_formatters": False, "formatters": True},
            None,
        ),
        pytest.param(
            ["--special-formatters"],
            {"attrs": False, "special_formatters": True, "formatters": False},
            lambda items: all(item[-1] == ":" for item in items),
        ),
    ],
)
def test_formatters_command_options(
    mocker: MockerFixture,
    args: Sequence[str],
    formatters_kwargs: dict[str, bool],
    output_check: Callable[[Collection[str]], Any] | None,
    capsys: pytest.CaptureFixture,
) -> None:
    mocked = mocker.spy(DefaultFormatters, "formatters_it")
    fedrq.cli.main(["formatters", *args])
    mocked.assert_called_once_with(**formatters_kwargs)
    out, err = capsys.readouterr()
    assert not err
    if output_check:
        output_check(out.splitlines())
