# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.cli


@pytest.mark.skip(
    "This test loads rawhide metadata and is expensive. We already load f37."
)
@pytest.mark.no_rpm_mock
def test_pkgs_basic_rawhide(capsys, target_cpu):
    fedrq.cli.main(["pkgs", "bash", "-Fna", "--sc"])
    stdout, stderr = capsys.readouterr()
    assert sorted(stdout.splitlines()) == sorted(["bash.src", f"bash.{target_cpu}"])


@pytest.mark.no_rpm_mock
def test_pkgs_forcearch(runs):
    stdout, stderr = runs(
        ["pkgs", "--forcearch", "s390x", "-F", "arch", "-b", "f37", "*"], False
    )
    assert not stderr
    assert set(stdout) == {"noarch", "s390x", "src"}
