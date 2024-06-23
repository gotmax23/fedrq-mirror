# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.cli

YT_DLP_SUPKGS = {
    "yt-dlp-bash-completion",
    "yt-dlp-zsh-completion",
    "yt-dlp-fish-completion",
}

ARGS = (
    (["yt-dlp"]),
    (["-P", "python3dist(yt-dlp)"]),
    (["yt-dlp.noarch"]),
)


@pytest.mark.no_rpm_mock
@pytest.mark.parametrize("args", ARGS)
def test_whatrequires_exclude_subpackages_f39(capsys, args):
    fedrq.cli.main(
        ["whatrequires", "-b", "f39", "-r", "@release", "--sc", "-X", "-Fname", *args]
    )
    stdout, stderr = capsys.readouterr()
    stdout_lines = set(stdout.splitlines())
    assert not (stdout_lines & YT_DLP_SUPKGS)
    assert "celluloid" in stdout_lines
    assert not stderr


@pytest.mark.no_rpm_mock
@pytest.mark.parametrize("args", ARGS)
def test_whatrequires_not_exclude_subpackages_f39(capsys, args):
    fedrq.cli.main(
        ["whatrequires", "-b", "f39", "-r", "@release", "--sc", "-Fname", *args]
    )
    stdout, stderr = capsys.readouterr()
    stdout_lines = set(stdout.splitlines())
    assert stdout_lines & YT_DLP_SUPKGS
    assert "celluloid" in stdout_lines
    assert not stderr


@pytest.mark.no_rpm_mock
def test_whatrequires_resolve(capsys):
    """
    Ensure that SRPM names are not considered when resolving Provides
    E.g. python-setuptools should resolve to python3-setuptools.noarch
    (Provides python-setuptools) instead of python-setuptools.src.
    """
    fedrq.cli.main(
        [
            "whatrequires",
            "-b",
            "f39",
            "-r",
            "@release",
            "-P",
            "-Fna",
            "python-setuptools",
        ]
    )
    stdout, stderr = map(lambda f: f.splitlines(), capsys.readouterr())
    # 3700 as of 2023-01-23. Le
    assert len(stdout) > 3000
    assert "python-pip.src" in stdout and "yt-dlp.src" in stdout
    assert not stderr
