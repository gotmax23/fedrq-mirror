# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli

YT_DLP_SUPKGS = [
    "yt-dlp-bash-completion",
    "yt-dlp-fish-completion",
    "yt-dlp-zsh-completion",
]


@pytest.mark.no_rpm_mock
def test_subpkgs_match1(capsys):
    fedrq.cli.main(["subpkgs", "yt-dlp", "--match", "*completion", "-F", "name"])
    stdout, stderr = capsys.readouterr()
    assert stdout.splitlines() == YT_DLP_SUPKGS
    assert not stderr


@pytest.mark.no_rpm_mock
def test_subpkgs_match2(capsys):
    # Find the source packages that contain a subpackage that match '*-devel'
    fedrq.cli.main(
        [
            "subpkgs",
            "containerd",
            "moby-engine",
            "--match",
            "*-devel",
            "-F",
            "source_name",
        ]
    )
    stdout, stderr = capsys.readouterr()
    assert stdout.splitlines() == ["containerd"]
    assert not stderr
