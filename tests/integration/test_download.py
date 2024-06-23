# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from pathlib import Path

import pytest

import fedrq.cli


@pytest.mark.no_rpm_mock
@pytest.mark.xfail(reason="My mirror 404s")
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
