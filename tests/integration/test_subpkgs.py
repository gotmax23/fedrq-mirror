# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.cli

YT_DLP_SUPKGS = [
    "yt-dlp-bash-completion",
    "yt-dlp-fish-completion",
    "yt-dlp-zsh-completion",
]


@pytest.mark.no_rpm_mock
def test_subpkgs_match1(capsys):
    fedrq.cli.main(
        ["subpkgs", "-b", "f37", "yt-dlp", "--match", "*completion", "-F", "name"]
    )
    stdout, stderr = capsys.readouterr()
    assert sorted(stdout.splitlines()) == YT_DLP_SUPKGS
    assert not stderr


@pytest.mark.no_rpm_mock
def test_subpkgs_match2(capsys):
    # Find the source packages that contain a subpackage that match '*-devel'
    fedrq.cli.main(
        [
            "subpkgs",
            "ansible-core",
            "moby-engine",
            "python-pip",
            "yt-dlp",
            "gh",  # no matches
            "-M",
            "*-fish-completion",
            "-M",
            "*-doc",
            "-Fname",
        ]
    )
    stdout, stderr = capsys.readouterr()
    assert stdout.splitlines() == [
        "ansible-core-doc",
        "moby-engine-fish-completion",
        "python-pip-doc",
        "yt-dlp-fish-completion",
    ]
    assert not stderr
