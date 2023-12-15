# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.config
from fedrq.backends.base import BackendMod, RepoqueryBase


def test_load_changelogs(default_backend: BackendMod):
    bm = default_backend.BaseMaker()
    config = fedrq.config.get_config()
    release = config.get_release("f37")
    bm.load_release_repos(release)
    expected_repos = [
        "fedora",
        "fedora-source",
        "updates",
        "updates-source",
    ]
    if default_backend.BACKEND == "dnf":
        bm.load_changelogs()
        enabled = list(bm.base.repos.iter_enabled())
        assert sorted(repo.id for repo in enabled) == expected_repos
        for key in expected_repos:
            assert bm.base.repos[key].load_metadata_other is True
        bm.load_changelogs(False)
        for key in expected_repos:
            assert bm.base.repos[key].load_metadata_other is False
    else:
        old = sorted(bm.base.get_config().optional_metadata_types)
        assert "other" not in old
        bm.load_changelogs(False)
        assert sorted(bm.base.get_config().optional_metadata_types) == old
        bm.load_changelogs()
        expected = sorted((*old, "other"))
        assert expected == sorted(bm.base.get_config().optional_metadata_types)
        bm.load_changelogs(False)
        assert sorted(bm.base.get_config().optional_metadata_types) == old


def test_bm_enable_disable(
    repo_test_rq: RepoqueryBase, default_backend: BackendMod
) -> None:
    bm = default_backend.BaseMaker(repo_test_rq.base)
    assert bm.repolist(True) == ["testrepo1"]
    bm.disable_repo("testrepo1")
    assert not bm.repolist(True)
    bm.enable_repos(["testrepo1"])

    with pytest.raises(
        ValueError, match="does-not-exist repo definition was not found."
    ):
        bm.disable_repo("does-not-exist", ignore_missing=False)


def test_bm_backend_property(default_backend: BackendMod) -> None:
    assert default_backend.BaseMaker().backend == default_backend
