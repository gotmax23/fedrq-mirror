# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli


def test_disablerepo_wildcard(patch_config_dirs, capsys):
    fedrq.cli.main(["pkgs", "--disablerepo=*", "*"])
    out, err = capsys.readouterr()
    assert not out and not err


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["-r", "testrepo1"]),
        pytest.param(["--disablerepo=*", "-e", "testrepo1"]),
        pytest.param(["--disablerepo=*", "--enablerepo", "base"]),
        pytest.param(["--disablerepo=*", "--enablerepo", "@base"]),
    ],
)
def test_repo_by_real_name(patch_config_dirs, capsys, args):
    fedrq.cli.main(["pkgs", *args, "-F", "repoid", "*"])
    out, err = capsys.readouterr()
    assert set(out.splitlines()) == {"testrepo1"}
    assert not err
