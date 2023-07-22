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
        pytest.skip(reason="This test checks libdnf5 functionality")


@pytest.mark.filterwarnings("error")
def test_libdnf5_deprecation():
    import fedrq.backends.libdnf5.backend as b

    with pytest.warns(match="Support for libdnf5 versions < 5.0.12 is deprecated."):
        b._deprecation_warn()
    # Should only warn once
    b._deprecation_warn()
