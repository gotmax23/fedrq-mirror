# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import fedrq.config


def test_source_repos_formatter():
    config = fedrq.config.get_config()
    release = config.get_release("f37", "@repo:fedora")
    bm = config.backend_mod.BaseMaker()
    bm.load_release_repos(release)
    assert bm.repolist(True) == ["fedora"]
    release.release_config.repogs.get_repo("@source-repos").load(bm, config, release)
    assert sorted(bm.repolist(True)) == sorted(["fedora", "fedora-source"])
