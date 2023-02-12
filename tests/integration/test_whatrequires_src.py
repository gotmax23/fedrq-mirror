# Copyright (C) 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest


@pytest.mark.no_rpm_mock
@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["ansible-core"]),
        pytest.param(["ansible-core.src"]),
    ],
)
def test_whatrequires_src_integration(runs, args):
    stdout, stderr = runs(["wrsrc", "-b", "f37", "-Fna", *args], False)
    assert not stderr
    assert any(p.startswith("ansible-collection") for p in stdout)
    assert {"ansible-packaging.noarch", "ansible.noarch", "ansible.src"} & set(stdout)


@pytest.mark.no_rpm_mock
def test_whatrequires_src_integration_exclude(runs):
    stdout, stderr = runs(
        ["wrsrc", "-b", "f37", "-Fsource", "-X", "ansible-packaging"], False
    )
    assert not stderr
    assert {
        "ansible-collection-ansible-posix",
        "ansible-collection-community-general",
    } & set(stdout)
    assert "ansible-packaging" not in stdout


@pytest.mark.no_rpm_mock
def test_whatrequires_src_integration_exclude_control(runs):
    stdout, stderr = runs(
        ["wrsrc", "-b", "f37", "-Fsource", "ansible-packaging"], False
    )
    assert not stderr
    assert {
        "ansible-collection-ansible-posix",
        "ansible-collection-community-general",
    } & set(stdout)
    assert "ansible-packaging" in stdout
