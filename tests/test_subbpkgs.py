import pytest

import fedrq.cli


def run_command2(args, capsys):
    fedrq.cli.main(["subpkgs", "-b", "tester", *args])
    stdin, stdout = capsys.readouterr()
    return stdin.splitlines(), stdout.splitlines()


def test_subpkgs_basic(capsys: pytest.CaptureFixture, patch_config_dirs):
    out = run_command2(["packagea", "-F", "name"], capsys)
    assert out[0] == ["packagea", "packagea-sub"]
    assert not out[1]


def test_subpkgs_specific_version(
    capsys: pytest.CaptureFixture, patch_config_dirs, target_cpu
):
    out = run_command2(["packageb-11111:2-1.fc36.src"], capsys)
    expected = [
        f"packageb-11111:2-1.fc36.{target_cpu}",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]

    assert out[0] == expected
    assert not out[1]


def test_subpkg_latest(capsys: pytest.CaptureFixture, patch_config_dirs):
    """
    --latest=1 is the default, but let's test it anyways
    """
    out = run_command2(["packageb", "--latest", "1", "-F", "nv"], capsys)
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
def test_subpkg_all(
    largs: list[str], capsys: pytest.CaptureFixture, patch_config_dirs, target_cpu
):
    expected2 = [
        f"packageb-1-1.fc36.{target_cpu}",
        f"packageb-11111:2-1.fc36.{target_cpu}",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]
    out2 = run_command2([*largs, "packageb"], capsys)
    assert out2[0] == expected2
    assert not out2[1]


def test_subpkg_noarch(capsys: pytest.CaptureFixture, patch_config_dirs):
    out = run_command2(
        ["packagea.src", "packageb.src", "-l=a", "--arch=noarch"], capsys
    )
    expected = [
        "packagea-1-1.fc36.noarch",
        "packagea-sub-1-1.fc36.noarch",
        "packageb-sub-1-1.fc36.noarch",
        "packageb-sub-11111:2-1.fc36.noarch",
    ]
    assert out[0] == expected
    assert not out[1]


def test_subpkg_x86_64(capsys: pytest.CaptureFixture, patch_config_dirs, target_cpu):
    out = run_command2(["packagea", "packageb", "-A", "x86_64", "-l", "ALL"], capsys)
    expected = [
        f"packageb-1-1.fc36.{target_cpu}",
        f"packageb-11111:2-1.fc36.{target_cpu}",
    ]
    assert out[0] == expected
    assert not out[1]
