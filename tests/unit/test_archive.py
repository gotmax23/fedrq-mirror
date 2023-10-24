# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import re
from pathlib import Path

import pytest

from fedrq._archive import RPMArchive, RPMArchiveError


def test_archive_extract_specfile(tmp_path: Path, data_path: Path):
    repo1 = data_path / "repos/repo1/"
    srpm = repo1 / "repo/SRPMS/specs/packageb-1-1.fc36.src.rpm"
    with RPMArchive(srpm) as archive:
        archive.extract_specfile(tmp_path)

    expected_spec = repo1 / "specs/packageb.spec"
    gotten = tmp_path / "packageb.spec"
    assert expected_spec.read_bytes() == gotten.read_bytes()


def test_archive_extract_specfile_error(
    tmp_path: Path, data_path: Path, target_cpu: str
):
    repo1 = data_path / "repos/repo1/"
    invalid = repo1 / f"repo/RPMS/specs/packageb-1-1.fc36.{target_cpu}.rpm"
    assert invalid.is_file()
    dest = tmp_path / "abc"
    dest.mkdir()
    with RPMArchive(invalid) as archive:  # noqa SIM177
        with pytest.raises(
            RPMArchiveError, match=re.escape(f"{archive} is not a source rpm")
        ):
            archive.extract_specfile(dest)
    assert next(dest.iterdir(), None) is None
