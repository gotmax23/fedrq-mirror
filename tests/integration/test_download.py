# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest

import fedrq.cli


@pytest.mark.no_rpm_mock
# TODO: Implement downloader that tries multiple mirrors.
# We don't want to download additional metadata for a newer Fedora during tests
# in addition to f39 that we already download.
@pytest.mark.xfail(reason="Download from EOL Fedora is flaky.")
def test_download_spec(tmp_path: Path):
    fedrq.cli.main(
        [
            "download-spec",
            "ansible-core",
            "-b",
            "f39",
            "-r",
            "@release",
            "-y",
            "-o",
            str(tmp_path),
        ]
    )
    assert (tmp_path / "ansible-core.spec").exists()
