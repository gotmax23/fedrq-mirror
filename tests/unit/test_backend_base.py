# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Generic repoquery backend tests
"""

from __future__ import annotations

from fedrq.backends.base import BackendMod

BACKEND_MEMBERS: set[str] = set(BackendMod.__annotations__)


def test_repoquery_interface():
    """
    Ensure the fedrq.repoquery module wrapper implements the full backend
    interface
    """
    import fedrq.repoquery

    assert set(dir(fedrq.repoquery)) & BACKEND_MEMBERS == BACKEND_MEMBERS


def test_backend_interface(default_backend):
    """
    Ensure the current backend implements the full backend interface
    """

    assert set(dir(default_backend)) & BACKEND_MEMBERS == BACKEND_MEMBERS
