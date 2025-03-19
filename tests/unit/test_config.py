# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import re

import pytest

from fedrq.backends.base import BackendMod, PackageCompat, RepoqueryBase
from fedrq.config import RQConfig, _warn_extra_configs


def test_get_rq(
    repo_test_config: RQConfig,
    repo_test_rq: RepoqueryBase[PackageCompat],
    default_backend: BackendMod,
) -> None:
    """
    Ensure get_rq() and its related methods select the correct backend
    """
    # Ensure the correct backend is used
    assert repo_test_rq.backend == default_backend
    assert repo_test_config.backend == default_backend.BACKEND

    # Check the backend specific methods, as well
    rq2: RepoqueryBase = {
        "dnf": repo_test_config.get_dnf_rq,
        "libdnf5": repo_test_config.get_libdnf5_rq,
    }[default_backend.BACKEND]()
    assert repo_test_config.backend == default_backend.BACKEND
    assert isinstance(rq2, type(repo_test_rq))
    assert isinstance(rq2, RepoqueryBase)
    assert isinstance(rq2, default_backend.Repoquery)


def test_warn_extra_configs() -> None:
    with pytest.warns(
        UserWarning,
        match=re.compile(
            re.escape("Unknown config options found in test: ['abc', 'xyz']")
        ),
    ):
        _warn_extra_configs(dict(abc="value", xyz="value", backend="dnf"), "test")
