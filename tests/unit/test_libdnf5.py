# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Test libdnf5-specific backend code
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from fedrq.config import RQConfig

if TYPE_CHECKING:
    from fedrq.backends.base import (
        BackendMod,
        PackageCompat,
        PackageQueryCompat,
        RepoqueryBase,
    )
    from fedrq.backends.libdnf5.backend import Package, PackageQuery, Repoquery


@pytest.fixture(autouse=True)
def skip_mod(default_backend: BackendMod):
    if default_backend.BACKEND != "libdnf5":
        pytest.skip("This test checks libdnf5 functionality")


def test_libdnf5_backend_types_subclass(repo_test_config: RQConfig):
    """
    Ensure that the libdnf5 Repoquery implementation type checks with the
    RepoqueryBase, PackageQueryCompat, and PackageCompat subclasses.
    (This test is here so mypy can check it.)
    """
    rq: Repoquery = repo_test_config.get_libdnf5_rq()
    package: Package = rq.get_package("packagea")
    assert package
    query: PackageQuery = rq.query()
    query = rq.arch_filter(query)
    query = rq.arch_filterm(query)
    query = rq.resolve_pkg_specs([])
    query = rq.get_subpackages(query)


def test_libdnf5_backend_types_baseclass(repo_test_config: RQConfig):
    """
    Ensure that the libdnf5 Repoquery implementation type checks with the
    RepoqueryBase, PackageQueryCompat, and PackageCompat baseclasses.
    (This test is here so mypy can check it.)
    """
    rq: RepoqueryBase = repo_test_config.get_libdnf5_rq()
    package: PackageCompat = rq.get_package("packagea")
    assert package
    query: PackageQueryCompat = rq.query()
    query = rq.arch_filter(query)
    query = rq.arch_filterm(query)
    query = rq.resolve_pkg_specs([])
    query = rq.get_subpackages(query)


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
