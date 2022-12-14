# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli


def run_command2(args, capsys, *, return_tuples=False, cachedir=None):
    if cachedir:
        args.append(f"--cachedir={cachedir}")
    fedrq.cli.main(["whatrequires", "-b", "tester", *args])
    stdin, stdout = capsys.readouterr()
    result = stdin.splitlines(), stdout.splitlines()
    if return_tuples:
        result = tuple(tuple(r) for r in result)
    return result


def test_whatrequires_exact(
    capsys,
    repo_test_tmpdir,
    patch_config_dirs,
):
    output = run_command2(["package(b)"], capsys, cachedir=repo_test_tmpdir)
    output2 = run_command2(["package(b)", "-E"], capsys, cachedir=repo_test_tmpdir)
    assert output == output2
    assert output[0] == ["packageb-sub-11111:2-1.fc36.noarch"]
    assert not output[1]


def test_whatrequires_name(
    capsys,
    repo_test_tmpdir,
    patch_config_dirs,
):
    output = run_command2(
        ["packageb", "-l", "a", "-F", "name"], capsys, cachedir=repo_test_tmpdir
    )
    assert output[0] == ["packagea"] * 2 + ["packageb-sub"] * 2
    assert not output[1]


def test_whatrequires_resolve_b(
    capsys,
    repo_test_tmpdir,
    patch_config_dirs,
):
    output = run_command2(
        ["package(b)", "-l", "a", "-P"],
        capsys,
        return_tuples=True,
        cachedir=repo_test_tmpdir,
    )
    output1 = run_command2(
        ["vpackage(b)", "-l", "a", "-P"],
        capsys,
        return_tuples=True,
        cachedir=repo_test_tmpdir,
    )
    output2 = run_command2(
        ["packageb", "-l", "a", "-P"],
        capsys,
        return_tuples=True,
        cachedir=repo_test_tmpdir,
    )
    output3 = run_command2(
        ["packageb", "-l", "a"], capsys, return_tuples=True, cachedir=repo_test_tmpdir
    )
    output4 = run_command2(
        ["/usr/share/packageb", "-l", "a", "-P"],
        capsys,
        return_tuples=True,
        cachedir=repo_test_tmpdir,
    )
    outputs = {output[0], output1[0], output2[0], output3[0], output4[0]}
    assert output[0] == (
        "packagea-1-1.fc36.noarch",
        "packagea-1-1.fc36.src",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    )
    assert len(outputs) == 1
    assert not output[1]


@pytest.mark.parametrize(
    "args",
    (
        (["packagea", "-E"]),
        (["packagea", "-P"]),
        (["package(a)", "-P"]),
        (["vpackage(a)", "-P"]),
        (["/usr/share/packagea", "-P"]),
    ),
)
def test_whatrequires_resolve_a(capsys, repo_test_tmpdir, patch_config_dirs, args):
    output = run_command2(args + ["-F", "nv"], capsys, cachedir=repo_test_tmpdir)
    assert output[0] == ["packagea-sub-1"]
    assert not output[1]


def test_whatrequires_versioned_resolve(capsys, repo_test_tmpdir, patch_config_dirs):
    output = run_command2(
        [
            "vpackage(b) = 11111:2-1.fc36",
            "-P",
            "-l",
            "all",
        ],
        capsys,
        cachedir=repo_test_tmpdir,
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
        (["package(a)", "-F", "attr:repo"], True),
        (["vpackage(a)", "-F", "source"], True),
        (["/usr/share/packagea", "-F", "attr:sourcerpm"], True),
        (["/usr/share/packageb", "-F", "nev"], True),
        # fedrq will resolve package names, so we need
        # to explicitly pass -E.
        (["packageb", "-F", "nv"], False),
        (["packageb.x86_64", "-F", "na"], False),
    ),
)
def test_exact_no_result(
    args, exact_optional, capsys, repo_test_tmpdir, patch_config_dirs
):
    """
    These work with -P, but should not print any results
    with --exact.
    """
    expected = ([], [])
    output = run_command2(args + ["-E"], capsys, cachedir=repo_test_tmpdir)
    assert output == expected
    if exact_optional:
        output2 = run_command2(args, capsys, cachedir=repo_test_tmpdir)
        assert output2 == expected


def test_whatrequires_breakdown(capsys, repo_test_tmpdir, patch_config_dirs):
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
    output = run_command2(
        ["-F", "breakdown", "packageb"], capsys, cachedir=repo_test_tmpdir
    )
    assert output[0] == expected
    assert not output[1]
