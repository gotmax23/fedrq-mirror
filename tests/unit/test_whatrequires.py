# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli


@pytest.fixture
def run_command(capsys, patch_config_dirs):
    def runner(args, *, return_tuples=False):
        fedrq.cli.main(["whatrequires", "--sc", *args])
        stdout, stderr = capsys.readouterr()
        result = stdout.splitlines(), stderr.splitlines()
        if return_tuples:
            result = tuple(tuple(r) for r in result)
        return result

    return runner


def test_whatrequires_exact(run_command):
    output = run_command(["package(b)"])
    output2 = run_command(["package(b)", "-E"])
    assert output == output2
    assert output[0] == ["packageb-sub-11111:2-1.fc36.noarch"]
    assert not output[1]


def test_whatrequires_name(run_command):
    output = run_command(["packageb", "-l", "a", "-F", "name"])
    assert output[0] == ["packagea"] * 2 + ["packageb-sub"] * 2
    assert not output[1]


@pytest.mark.parametrize(
    "args",
    (
        pytest.param(["package(b)", "-l", "a", "-P"]),
        pytest.param(["vpackage(b)", "-l", "a", "-P"]),
        pytest.param(["packageb", "-l", "a", "-P"]),
        pytest.param(
            ["packageb", "-l", "a"],
        ),
        pytest.param(["/usr/share/packageb", "-l", "a", "-P", "-Lalways"]),
    ),
)
def test_whatrequires_resolve_b(run_command, args):
    stdout, stderr = run_command(args, return_tuples=True)
    assert stdout == (
        "packagea-1-1.fc36.noarch",
        "packagea-1-1.fc36.src",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    )
    assert not stderr


@pytest.mark.parametrize(
    "args",
    (
        (["packagea", "-E"]),
        (["packagea", "-P"]),
        (["package(a)", "-P"]),
        (["vpackage(a)", "-P"]),
        (["/usr/share/packagea", "-P", "-Lalways"]),
    ),
)
def test_whatrequires_resolve_a(run_command, args):
    output = run_command(args + ["-F", "nv"])
    assert output[0] == ["packagea-sub-1"]
    assert not output[1]


def test_whatrequires_versioned_resolve(run_command):
    output = run_command(
        [
            "vpackage(b) = 11111:2-1.fc36",
            "-P",
            "-l",
            "all",
        ]
    )
    assert output[0] == [
        "packagea-1-1.fc36.noarch",
        "packagea-1-1.fc36.src",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]
    assert not output[1]


@pytest.mark.parametrize(
    "args, exact_optional",
    (
        # Choose a random formatter to check that they don't fail
        # when no packages are provided.
        (["package(a)", "-F", "attr:repoid"], True),
        (["vpackage(a)", "-F", "source"], True),
        (["/usr/share/packagea", "-F", "attr:sourcerpm", "-Lalways"], True),
        (["/usr/share/packageb", "-F", "nev", "-Lalways"], True),
        # fedrq will resolve package names, so we need
        # to explicitly pass -E.
        (["packageb", "-F", "nv"], False),
        (["packageb.{target_cpu}", "-F", "na"], False),
    ),
)
def test_exact_no_result(args, exact_optional, run_command, target_cpu):
    """
    These work with -P, but should not print any results
    with --exact.
    """
    expected = ([], [])
    args = [arg.format(target_cpu=target_cpu) for arg in args]
    output = run_command(args + ["-E"])
    assert output == expected
    if exact_optional:
        output2 = run_command(args)
        assert output2 == expected


def test_whatrequires_breakdown(run_command):
    expected = """\
Runtime:
packagea
packageb-sub
    2 total runtime dependencies

Buildtime:
packagea
    1 total buildtime dependencies

All SRPM names:
packagea
packageb
    2 total SRPMs""".splitlines()
    output = run_command(["-F", "breakdown", "packageb"])
    assert output[0] == expected
    assert not output[1]


def test_whatrequires_exclude_subpackages(run_command):
    expected = ["packagea.noarch", "packagea.src"]
    stdout, stderr = run_command(["-X", "-F", "na", "packageb"])
    assert not stderr
    assert stdout == expected
