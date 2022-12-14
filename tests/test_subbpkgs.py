# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli


@pytest.fixture
def run_command(capsys, repo_test_tmpdir, patch_config_dirs):
    def runner(args):
        fedrq.cli.main(
            ["subpkgs", "--cachedir", repo_test_tmpdir, "-b", "tester", *args]
        )
        stdout, stderr = capsys.readouterr()
        result = stdout.splitlines(), stderr.splitlines()
        return result

    return runner


def test_subpkgs_basic(run_command):
    out = run_command(["packagea", "-F", "name"])
    assert out[0] == ["packagea", "packagea-sub"]
    assert not out[1]


def test_subpkgs_specific_version(run_command, target_cpu):
    out = run_command(["packageb-11111:2-1.fc36.src"])
    expected = [
        f"packageb-11111:2-1.fc36.{target_cpu}",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]

    assert out[0] == expected
    assert not out[1]


def test_subpkg_latest(run_command):
    """
    --latest=1 is the default, but let's test it anyways
    """
    out = run_command(["packageb", "--latest", "1", "-F", "nv"])
    expected1 = [
        "packageb-2",
        "packageb-sub-2",
    ]
    assert out[0] == expected1
    assert not out[1]


@pytest.mark.parametrize(
    "largs",
    (
        ["--latest=a"],
        ["--latest=all"],
    ),
)
def test_subpkg_all(largs: list[str], run_command, target_cpu):
    expected2 = [
        f"packageb-1-1.fc36.{target_cpu}",
        f"packageb-11111:2-1.fc36.{target_cpu}",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]
    out2 = run_command([*largs, "packageb"])
    assert out2[0] == expected2
    assert not out2[1]


def test_subpkg_noarch(run_command):
    out = run_command(["packagea.src", "packageb.src", "-l=a", "--arch=noarch"])
    expected = [
        "packagea-1-1.fc36.noarch",
        "packagea-sub-1-1.fc36.noarch",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]
    assert out[0] == expected
    assert not out[1]


def test_subpkg_x86_64(run_command, target_cpu):
    out = run_command(["packagea", "packageb", "-A", "x86_64", "-l", "ALL"])
    expected = [
        f"packageb-1-1.fc36.{target_cpu}",
        f"packageb-11111:2-1.fc36.{target_cpu}",
    ]
    assert out[0] == expected
    assert not out[1]
