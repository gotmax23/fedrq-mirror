# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Tests for experimental comps code in backends
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from fedrq.backends.base import BackendMod
from fedrq.backends.base.experimental import EnvironmentQuery, GroupQuery
from fedrq.config import get_config


def default_backend_experimental(default_backend: BackendMod):
    if default_backend.BACKEND == "dnf":
        from fedrq.backends.dnf.backend import experimental
    elif default_backend.BACKEND == "libdnf5":
        from fedrq.backends.libdnf5.backend import (  # type: ignore[no-redef]
            experimental,
        )
    else:
        raise ValueError
    return experimental


@pytest.fixture(scope="module")
def f39_base() -> Any:
    return get_config().get_rq("f39").base


@pytest.fixture
def new_group_query(
    default_backend: BackendMod, f39_base: Any
) -> Callable[..., GroupQuery]:
    experimental = default_backend_experimental(default_backend)
    return lambda: experimental.GroupQuery(f39_base)


@pytest.fixture
def new_env_query(
    default_backend: BackendMod, f39_base: Any
) -> Callable[..., EnvironmentQuery]:
    experimental = default_backend_experimental(default_backend)
    return lambda: experimental.EnvironmentQuery(f39_base)


def test_group_query(new_group_query: Callable[..., GroupQuery]) -> None:
    group_query = new_group_query()
    group_query_new = group_query.filterm(name="Buildsystem building group")
    # Filtering is done is place
    assert group_query_new is group_query
    assert len(group_query) == 1
    group = next(iter(group_query))
    group_query = new_group_query()
    group_query.filter_groupid("buildsys-build")
    group_query.filterm(groupid__eq="buildsys-build")
    assert len(group_query) == 1
    assert next(iter(group_query)) == group
    group_query.filterm(groupid__neq="buildsys-build")
    assert len(group_query) == 0


def test_group_query_filters(
    default_backend: BackendMod, new_group_query: Callable[..., GroupQuery]
) -> None:
    exp = default_backend_experimental(default_backend)
    group_query = new_group_query()
    group_query.filter_package_name(["rpmlint", "podman"])
    group_list = sorted(group_query)
    assert [group.groupid for group in group_list] == [
        "container-management",
        "rpm-development-tools",
    ]
    assert group_list[0] < group_list[1]
    assert group_list[0] <= group_list[1]
    assert group_list[0] == group_list[0]
    assert group_list[0] <= group_list[0]
    assert group_list[0] != group_list[1]
    assert group_list[1] > group_list[0]
    assert group_list[1] >= group_list[0]

    assert len(group_query) == 2
    group_query.remove(group_list[0])
    assert len(group_query) == 1
    assert group_query
    group_query.clear()
    assert len(group_query) == 0
    assert not group_query

    group_query2 = new_group_query()
    group_query2.filter_uservisible(False)
    assert "GNOME" in {group.name for group in group_query2}

    # Test set operations
    group_query = new_group_query()
    group_query2 |= group_query
    assert len(group_query2) == len(group_query)
    assert isinstance(group_query, exp.GroupQuery)

    group_query -= group_query2  # pyright: ignore[reportOperatorIssue]
    assert next(iter(group_query2)) not in group_query
    assert isinstance(group_query, exp.GroupQuery)

    group_query &= group_query2  # pyright: ignore[reportOperatorIssue]
    assert len(group_query) == 0
    assert isinstance(group_query, exp.GroupQuery)


def test_group(
    default_backend: BackendMod, new_group_query: Callable[..., GroupQuery]
) -> None:
    experimental = default_backend_experimental(default_backend)
    group_query = new_group_query()

    group = next(iter(group_query.filterm(groupid="container-management")))
    assert group.name == "Container Management"
    assert group.translated_name == group.name
    assert group.description == "Tools for managing Linux containers"
    assert group.translated_description == group.description
    assert not group.langonly
    assert group.uservisible
    # Check __hash__
    group_set = set(group_query)
    assert len(group_set) == len(group_query)

    packages = sorted(group.packages)
    defaults = group.get_packages_of_type(experimental.PackageType.DEFAULT)
    assert [package.name for package in defaults] == ["podman"]
    defaults = group.get_packages_of_type(~experimental.PackageType.OPTIONAL)
    assert [package.name for package in defaults] == ["podman"]

    podman = defaults[0]
    buildah = next(package for package in group.packages if package.name == "buildah")
    assert buildah < podman
    assert buildah <= podman
    assert buildah == buildah  # noqa: PLR0124
    assert podman > buildah
    assert podman >= buildah
    assert podman != buildah

    # Check __hash__
    package_set = set(packages)
    assert len(package_set) == len(packages)

    packages2 = sorted(
        group.get_packages_of_type(
            experimental.PackageType.DEFAULT | experimental.PackageType.OPTIONAL
        )
    )
    # The group only contains DEFAULT and OPTIONAL packages, so these should be
    # the same
    assert packages2 == packages


def test_environment(
    default_backend: BackendMod, new_env_query: Callable[..., EnvironmentQuery]
) -> None:
    exp = default_backend_experimental(default_backend)
    env_query = new_env_query()
    env_query2 = new_env_query()

    env_query.filter_environmentid("*-desktop-*", exp.QueryCmp.GLOB)
    assert all(e.environmentid.endswith("-desktop-environment") for e in env_query)
    env_query2.filterm(name="Basic Desktop")
    assert len(env_query2) == 1

    env_query.filterm(name=["Basic Desktop", "Budgie Desktop"])
    assert len(env_query) == 2
    q_sorted = sorted(env_query)
    basic = q_sorted[0]
    assert basic.environmentid == "basic-desktop-environment"
    budgie = q_sorted[1]
    assert budgie.environmentid == "budgie-desktop-environment"
    assert basic < budgie
    assert basic <= budgie
    assert basic == basic  # noqa: PLR0124
    assert budgie > basic
    assert budgie >= basic
    assert budgie != basic

    # Test the methods for set operations here
    # The binary operators are tested above
    env_query = env_query.intersection(env_query2)
    env = next(iter(env_query))
    # assert env == basic  # TODO: This doesn't work with libdnf5
    assert len(env_query) == 1
    assert env.name == "Basic Desktop"
    assert env.translated_name == env.name
    assert env.description == "X Window System with a choice of window manager."
    assert env.translated_description == env.description
    assert env in env_query

    old_len = len(env_query2)
    env_query2.remove(env)
    assert env not in env_query2
    assert len(env_query2) == old_len - 1
    env_query2.add(env)

    env_query2 = env_query2.difference(env_query)
    assert env not in env_query2
    assert len(env_query2) == old_len - 1
    env_query2.add(env)

    env_query_union = env_query.union(env_query2)
    env_query.update(env_query2)
    assert set(env_query) == set(env_query2) == set(env_query_union)

    for groups in (env.groupids, env.optional_groupids):
        firstgroup = next(iter(groups))
        assert isinstance(firstgroup, str)
        assert " " not in firstgroup  # It should be a space-less groupid

    assert env_query
    env_query.clear()
    assert not env_query
