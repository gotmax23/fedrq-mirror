# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Test libdnf5-specific backend code
"""

from __future__ import annotations

import pytest

from fedrq.backends.base import BackendMod


@pytest.fixture(autouse=True)
def skip_mod(default_backend: BackendMod):
    if default_backend.BACKEND != "libdnf5":
        pytest.skip("This test checks libdnf5 functionality")


def test_libdnf5_bm_load_filelists():
    import fedrq.backends.libdnf5.backend as b

    bm = b.BaseMaker()
    default_types = sorted(bm.conf.optional_metadata_types)
    assert "filelists" not in default_types
    bm.load_filelists(False)
    assert sorted(bm.conf.optional_metadata_types) == default_types
    bm.load_filelists(True)
    new = sorted((*default_types, "filelists"))
    assert sorted(bm.conf.optional_metadata_types) == new
