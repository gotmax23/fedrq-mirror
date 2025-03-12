# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later


"""
This module (and the other experimental modules in fedrq) are not meant for public use.
They are subject to breaking changes in minor releases and should not be relied
on by external code.
Once the functionality has stabilized, this code will be moved out of the
experimental namespace.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import IntEnum
from typing import TYPE_CHECKING, Any

import libdnf5
import libdnf5._comps
import libdnf5.common
import libdnf5.comps

# from . import libdnf5
from fedrq.backends.base import experimental as base

if TYPE_CHECKING:
    from typing_extensions import Self, Unpack


class PackageType(IntEnum):
    CONDITIONAL = libdnf5.comps.PackageType_CONDITIONAL
    DEFAULT = libdnf5.comps.PackageType_DEFAULT
    MANDATORY = libdnf5.comps.PackageType_MANDATORY
    OPTIONAL = libdnf5.comps.PackageType_OPTIONAL

    @classmethod
    def _from_int(cls, value: Any) -> PackageType:
        return {i: i for i in cls}[value]


class GroupPackage(libdnf5.comps.Package, base.GroupPackage):
    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def package_type(self) -> PackageType:
        return PackageType._from_int(self.get_type())

    def __gt__(self, other: Self) -> bool:
        return self._comptup() > other._comptup()

    def __ge__(self, other: Self) -> bool:
        return self._comptup() >= other._comptup()

    def __lt__(self, other: Self) -> bool:
        return self._comptup() < other._comptup()

    def __le__(self, other: Self) -> bool:
        return self._comptup() <= other._comptup()

    def _comptup(self) -> tuple[Any, ...]:
        return (self.name, self.package_type)

    if not getattr(libdnf5.comps.Package, "__hash__", None):

        def __hash__(self) -> int:
            return hash((self.name, self.package_type))


libdnf5._comps.Package_swigregister(GroupPackage)


class Group(libdnf5.comps.Group, base.Group):
    __lt__ = libdnf5.comps.Group.__lt__

    def __le__(self, other: Self) -> bool:
        return not (self > other)

    def __gt__(self, other: Self) -> bool:
        # Based on operator< impl in libdnf5/comps/group/group.cpp
        return self.groupid > other.groupid or self.get_repos() > other.get_repos()

    def __ge__(self, other: Self) -> bool:
        return not (self < other)

    @property
    def groupid(self) -> str:
        return self.get_groupid()

    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def description(self) -> str:
        return self.get_description()

    @property
    def translated_name(self) -> str:
        return self.get_translated_name()

    @property
    def translated_description(self) -> str:
        return self.get_translated_description()

    @property
    def langonly(self) -> bool:
        return self.get_langonly()

    @property
    def uservisible(self) -> bool:
        return self.get_uservisible()

    @property
    def packages(self) -> base.SimpleSequence[GroupPackage]:
        return self.get_packages()

    if not getattr(libdnf5.comps.Group, "__hash__", None):

        def __hash__(self) -> int:
            return hash((self.groupid, self.get_repos()))

    # Add annotations for methods provided by parent
    if TYPE_CHECKING:

        def get_packages(self) -> list[GroupPackage]:
            return []


libdnf5._comps.Group_swigregister(Group)


class QueryCmp(IntEnum):
    EQ = libdnf5.common.QueryCmp_EQ
    NEQ = libdnf5.common.QueryCmp_NEQ
    CONTAINS = libdnf5.common.QueryCmp_CONTAINS
    GLOB = libdnf5.common.QueryCmp_GLOB


class GroupQuery(libdnf5.comps.GroupQuery, base.GroupQuery):

    def difference(self, other) -> GroupQuery:
        """
        NOTE: Unlike normal Python sets, this modifies 'self' in place.
        """
        libdnf5.comps.GroupQuery.difference(self, other)
        return self

    __isub__ = difference

    def union(self, other) -> GroupQuery:
        """
        NOTE: This modifies 'self' in place.
        """
        self.update(other)
        return self

    __ior__ = union

    def intersection(self, other) -> GroupQuery:
        """
        NOTE: Unlike normal Python sets, this modifies 'self' in place.
        """
        libdnf5.comps.GroupQuery.intersection(self, other)
        return self

    __iand__ = intersection

    def __contains__(self, other) -> bool:
        return self.contains(other)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.empty()

    def filterm(self, **kwargs: Unpack[base.GroupQueryKwargs]) -> GroupQuery:
        base._filter_func(self, QueryCmp, **kwargs)
        return self

    if TYPE_CHECKING:

        # We register our subclass with swig so that the iterator contains our
        # Group subclass instead of the base Group class.
        # Let the type checker know that.
        def __iter__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ) -> Iterator[Group]:
            return
            yield


libdnf5._comps.GroupQuery_swigregister(GroupQuery)


class Environment(libdnf5.comps.Environment, base.Environment):
    __lt__ = libdnf5.comps.Environment.__lt__

    def __le__(self, other: Self) -> bool:
        return not (self > other)

    def __gt__(self, other: Self) -> bool:
        # Based on operator< impl in libdnf5/comps/group/group.cpp
        return (
            self.environmentid > other.environmentid
            or self.get_repos() > other.get_repos()
        )

    def __ge__(self, other: Self) -> bool:
        return not (self < other)

    @property
    def environmentid(self) -> str:
        return self.get_environmentid()

    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def description(self) -> str:
        return self.get_description()

    @property
    def translated_name(self) -> str:
        return self.get_translated_name()

    @property
    def translated_description(self) -> str:
        return self.get_translated_description()

    @property
    def groupids(self) -> base.SimpleSequence[str]:
        return self.get_groups()

    @property
    def optional_groupids(self) -> base.SimpleSequence[str]:
        return self.get_optional_groups()

    def __hash__(self) -> int:
        return hash((self.environmentid, tuple(self.get_repos())))


libdnf5._comps.Environment_swigregister(Environment)


class EnvironmentQuery(libdnf5.comps.EnvironmentQuery, base.EnvironmentQuery):

    def difference(self, other) -> EnvironmentQuery:
        """
        NOTE: Unlike normal Python sets, this modifies 'self' in place.
        """
        libdnf5.comps.EnvironmentQuery.difference(self, other)
        return self

    __isub__ = difference

    def union(self, other) -> EnvironmentQuery:
        """
        NOTE: This modifies 'self' in place.
        """
        self.update(other)
        return self

    __ior__ = union

    def intersection(self, other) -> EnvironmentQuery:
        """
        NOTE: Unlike normal Python sets, this modifies 'self' in place.
        """
        libdnf5.comps.EnvironmentQuery.intersection(self, other)
        return self

    __iand__ = intersection

    def __contains__(self, other) -> bool:
        return self.contains(other)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.empty()

    def filterm(
        self, **kwargs: Unpack[base.EnvironmentQueryKwargs]
    ) -> EnvironmentQuery:
        base._filter_func(self, QueryCmp, **kwargs)
        return self

    if TYPE_CHECKING:

        # We register our subclass with swig so that the iterator contains our
        # Environment subclass instead of the base Environment class.
        # Let the type checker know that.
        def __iter__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self,
        ) -> Iterator[Environment]:
            return
            yield


libdnf5._comps.EnvironmentQuery_swigregister(EnvironmentQuery)
