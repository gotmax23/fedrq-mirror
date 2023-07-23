# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import datetime

from fedrq.backends.base import ChangelogEntry, RepoqueryBase


def test_get_changelogs(repo_test_rq: RepoqueryBase):
    query = repo_test_rq.query()
    for package in query:
        evr = package.evr.split(".", 1)[0]
        expected = ChangelogEntry(
            text="- Dummy changelog entry",
            author=f"Maxwell G <maxwell@gtmx.me> - {evr}",
            date=datetime.date(2023, 7, 16),
        )
        entries = list(repo_test_rq.backend.get_changelogs(package))
        assert entries == [expected]
