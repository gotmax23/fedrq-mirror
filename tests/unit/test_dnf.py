# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Test dnf-specific backend code
"""

from __future__ import annotations

import pytest

from fedrq.backends.base import BackendMod


@pytest.fixture(autouse=True)
def skip_mod(default_backend: BackendMod):
    if default_backend.BACKEND != "dnf":
        pytest.skip("This test checks libdnf5 functionality")


def test_bm_set_var_invalid(default_backend: BackendMod):
    bm = default_backend.BaseMaker()
    with pytest.raises(KeyError, match="best is not a valid substitution"):
        bm.set_var("best", "")
