# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import fedrq.config
from fedrq.backends.base import BackendMod


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
