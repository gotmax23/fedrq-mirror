# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Generic repoquery backend tests
"""

from __future__ import annotations

from fedrq.backends.base import BackendMod, RepoqueryBase

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


def test_package_query_intersection(repo_test_rq: RepoqueryBase) -> None:
    packagea_query = repo_test_rq.query(name="packagea")
    source_query = repo_test_rq.query(arch="src")
    intersection = packagea_query.intersection(source_query)
    nas = [f"{package.name}.{package.arch}" for package in intersection]
    assert nas == ["packagea.src"]


def test_package_query_difference(repo_test_rq: RepoqueryBase) -> None:
    packagea_query = repo_test_rq.query(name="packagea")
    source_query = repo_test_rq.query(arch="src")
    difference = packagea_query.difference(source_query)
    nas = [f"{package.name}.{package.arch}" for package in difference]
    assert nas == ["packagea.noarch"]
