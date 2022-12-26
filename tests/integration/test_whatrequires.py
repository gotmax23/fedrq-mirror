# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

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
def test_whatrequires_exclude_subpackages_f37(capsys, args):
    fedrq.cli.main(["whatrequires", "-b", "f37", "--sc", "-X", "-Fname", *args])
    stdout, stderr = capsys.readouterr()
    stdout_lines = set(stdout.splitlines())
    assert not (stdout_lines & YT_DLP_SUPKGS)
    assert "celluloid" in stdout_lines
    assert not stderr


@pytest.mark.no_rpm_mock
@pytest.mark.parametrize("args", ARGS)
def test_whatrequires_not_exclude_subpackages_f37(capsys, args):
    fedrq.cli.main(["whatrequires", "-b", "f37", "--sc", "-Fname", *args])
    stdout, stderr = capsys.readouterr()
    stdout_lines = set(stdout.splitlines())
    assert stdout_lines & YT_DLP_SUPKGS
    assert "celluloid" in stdout_lines
    assert not stderr
