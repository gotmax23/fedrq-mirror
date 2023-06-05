# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.cli


def test_repolist(capsys: pytest.CaptureFixture):
    fedrq.cli.main(
        [
            "repolist",
            "--branch=rawhide",
            "--repos=buildroot",
            "--disablerepo=fedrq-koji-rawhide-source",
            "--enablerepo=@repo:fedrq-koji-rawhide-source",
        ]
    )
    out, err = capsys.readouterr()
    assert sorted(out.splitlines()) == [
        "fedrq-koji-rawhide",
        "fedrq-koji-rawhide-source",
    ]
    assert not err.strip()
