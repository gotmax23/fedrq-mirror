# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Generic backends tests
"""

from __future__ import annotations

import pytest

from fedrq.backends import get_default_backend
from fedrq.backends.base import BackendMod


def test_backends_no_allow_multiple_backends_per_process(
    default_backend: BackendMod,
) -> None:
    other_backends = {"dnf": "libdnf5", "libdnf5": "dnf"}
    other = other_backends[default_backend.BACKEND]
    with pytest.warns(
        UserWarning,
        match=f"Falling back to {default_backend.BACKEND}. {other} cannot be used.",
    ):
        assert (
            get_default_backend(other, allow_multiple_backends_per_process=False)
            == default_backend
        )
