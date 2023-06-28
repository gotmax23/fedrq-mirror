# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

import fedrq.cli


def test_download_spec(
    patch_config_dirs, tmp_path: Path, data_path: Path, capsys: CaptureFixture
):
    tmp_path /= "abc"
    tmp_path.mkdir()
    repo1 = data_path / "repos/repo1/"
    # srpm = repo1 / "repo/SRPMS/specs/packagea-1-1.fc36.src.rpm"
    expected_spec = repo1 / "specs/packagea.spec"

    fedrq.cli.main(["download-spec", "packagea", "-o", str(tmp_path), "-y"])
    gotten = tmp_path / "packagea.spec"
    assert list(tmp_path.iterdir()) == [gotten]
    assert expected_spec.read_bytes() == gotten.read_bytes()


def test_download(
    patch_config_dirs, tmp_path: Path, data_path: Path, capsys: CaptureFixture
):
    tmp_path /= "xyz"
    tmp_path.mkdir()
    repo = data_path / "repos/repo1/repo"
    expected = [
        repo / "SRPMS/specs/packagea-1-1.fc36.src.rpm",
        repo / "RPMS/specs/packagea-1-1.fc36.noarch.rpm",
    ]

    fedrq.cli.main(["download", "packagea", "-o", str(tmp_path), "-y"])
    gotten = tmp_path / "packagea.spec"
    assert len(list(tmp_path.iterdir())) == 2
    for expect in expected:
        gotten = tmp_path / expect.name
        assert expect.read_bytes() == gotten.read_bytes()
