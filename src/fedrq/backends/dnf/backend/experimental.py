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

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Sequence
from enum import IntEnum, IntFlag
from enum import auto as enum_auto
from fnmatch import fnmatch
from functools import cached_property
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import dnf
import dnf.comps

from fedrq._utils import enum_from_int
from fedrq.backends.base import experimental as base

if TYPE_CHECKING:
    from typing_extensions import Self, Unpack


def _check_same_base(obj: Any, other_base: Any) -> None:
    if other_base is not obj._base:  # pragma: no cover
        raise ValueError(
            f"Cannot perform operations with a {type(obj).__name__}"
            " associated with another Base object"
        )


class PackageType(IntEnum):
    CONDITIONAL = dnf.comps.CONDITIONAL
    DEFAULT = dnf.comps.DEFAULT
    MANDATORY = dnf.comps.MANDATORY
    OPTIONAL = dnf.comps.OPTIONAL


class GroupPackage(base.GroupPackage):
    """
    "Immutable" class representing a packge in a comps group
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: dnf.comps.Package):
        self._impl = impl

    @property
    def impl(self) -> dnf.comps.Package:
        return self._impl

    @property
    def name(self) -> str:
        return self.impl.name

    @property
    def package_type(self) -> PackageType:
        return enum_from_int(PackageType, self.impl.option_type)

    def __repr__(self) -> str:
        name, typ = self.name, self.package_type
        return f"GroupPackage<name={name!r}, package_type={typ!r}>"

    def __hash__(self) -> int:
        return hash(self._comptup)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, GroupPackage):  # pragma: no cover
            return False
        return self._comptup() == value._comptup()

    def __gt__(self, other: Self) -> bool:
        return self._comptup() > other._comptup()

    def __ge__(self, valueother: Self) -> bool:
        return self._comptup() >= valueother._comptup()

    def __lt__(self, other: Self) -> bool:
        return self._comptup() < other._comptup()

    def __le__(self, other: Self) -> bool:
        return self._comptup() <= other._comptup()

    def _comptup(self) -> tuple[Any, ...]:
        return (self.name, self.package_type)


class Group(base.Group):
    """
    "Immutable" class representing a comps group
    """

    __slots__ = ("_impl", "_base")

    def __init__(self, impl: dnf.comps.Group, base: dnf.Base) -> None:
        self._impl = impl
        self._base = base

    _check_same_base = _check_same_base

    def __hash__(self) -> int:
        return hash(self.groupid)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Group):  # pragma: no cover
            return False
        return self.groupid == other.groupid and self._base == other._base

    def __gt__(self, other: Group) -> bool:
        self._check_same_base(other._base)
        return self.groupid > other.groupid

    def __ge__(self, other: Group) -> bool:
        self._check_same_base(other._base)
        return self.groupid >= other.groupid

    def __lt__(self, other: Group) -> bool:
        self._check_same_base(other._base)
        return self.groupid < other.groupid

    def __le__(self, other: Group) -> bool:
        self._check_same_base(other._base)
        return self.groupid <= other.groupid

    @property
    def impl(self) -> dnf.comps.Group:
        return self._impl

    # @property
    # def base(self) -> dnf.Base:
    #     return self._base

    @property
    def groupid(self) -> str:
        return self._impl.id

    @property
    def name(self) -> str:
        return self._impl.name

    @property
    def description(self) -> str:
        return self._impl.desc

    @property
    def translated_name(self) -> str:
        return self._impl.ui_name

    @property
    def translated_description(self) -> str:
        return self._impl.ui_description

    @property
    def langonly(self) -> bool:
        return self._impl.lang_only

    @property
    def uservisible(self) -> bool:
        return self._impl.uservisible

    # pyright does not understand cached_property
    @cached_property
    def packages(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> Sequence[GroupPackage]:
        return tuple(map(GroupPackage, self._impl.packages_iter()))

    def get_packages_of_type(
        self, package_type: PackageType | int, /
    ) -> Sequence[GroupPackage]:
        packages: list[GroupPackage] = []
        for package in self.packages:
            if package.package_type & package_type:
                packages.append(package)
        return tuple(packages)


class QueryCmp(IntFlag):
    EQ = enum_auto()
    NEQ = enum_auto()
    CONTAINS = enum_auto()
    GLOB = enum_auto()


def _match_string_single(
    value: str,
    cmp: QueryCmp | int,
    pattern: str,
):
    cmps: dict[QueryCmp | int, Callable[[], bool]] = {
        QueryCmp.EQ: lambda: pattern == value,
        QueryCmp.NEQ: lambda: pattern != value,
        QueryCmp.CONTAINS: lambda: pattern in value,
        QueryCmp.GLOB: lambda: fnmatch(value, pattern),
    }
    try:
        cmp_function = cmps[cmp]
    except KeyError:  # pragma: no cover
        raise ValueError(f"Invalid cmp: {cmp}") from None
    return cmp_function()


def _match_string(
    values: base._StrIter, cmp: QueryCmp | int, patterns: base._StrIter
) -> bool:
    values = [values] if isinstance(values, str) else values
    patterns = [patterns] if isinstance(patterns, str) else patterns
    for value in values:
        for pattern in patterns:
            if _match_string_single(value, cmp, pattern):
                return True
    return False


_T = TypeVar("_T")


def _query_filter(
    items: Iterable[_T],
    getter: Callable[[Any], base._StrIter],
    patterns: base._StrIter,
    cmp: QueryCmp | int,
) -> Iterator[_T]:

    return (item for item in items if _match_string(getter(item), cmp, patterns))


def _query_update(
    items: _QuerySetBase[Any],
    getter: Callable[[Any], base._StrIter],
    patterns: base._StrIter,
    cmp: QueryCmp | int,
) -> None:
    filtered = _query_filter(items, getter, patterns, cmp)
    items._impl.intersection_update(filtered)


def _query_filter_bool(
    items: Iterable[_T], getter: Callable[[Any], bool], value: bool
) -> Iterator[_T]:
    # Explicitly cooerce into a bool because we're using if ... is
    value = bool(value)
    return (item for item in items if getter(item) is value)


def _query_update_bool(
    items: _QuerySetBase[Any], getter: Callable[[Any], bool], value: bool
) -> None:
    filtered = _query_filter_bool(items, getter, value)
    items._impl.intersection_update(filtered)


class _QuerySetBase(ABC, Generic[_T]):
    __slots__ = ("_base", "_impl")
    _base: dnf.Base
    _impl: set[_T]

    def __init__(self, base: dnf.Base, *, _impl: set[_T] | None = None) -> None:
        self._base = base
        self._impl = self._initial() if _impl is None else _impl

    _check_same_base = _check_same_base

    @abstractmethod
    def _initial(self) -> set[_T]: ...

    # @property
    # def base(self) -> dnf.Base:
    #     return self._base

    def __len__(self) -> int:
        return len(self._impl)

    def __contains__(self, key: object) -> bool:
        return key in self._impl

    def __iter__(self) -> Iterator[_T]:
        return iter(self._impl)

    # The the non-in-place set methods are not available in the libdnf5
    # version
    def __or__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        return type(self)(self._base, _impl=self._impl | other._impl)

    def __and__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        return type(self)(self._base, _impl=self._impl & other._impl)

    def __sub__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        return type(self)(self._base, _impl=self._impl - other._impl)

    def __ior__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        self._impl |= other._impl
        return self

    def __iand__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        self._impl &= other._impl
        return self

    def __isub__(self, other: Self) -> Self:
        self._check_same_base(other._base)
        self._impl -= other._impl
        return self

    def difference(self, other: Self) -> Self:
        return self - other

    def union(self, other: Self) -> Self:
        return self | other

    def intersection(self, other: Self) -> Self:
        return self & other

    def add(self, other: _T) -> None:
        self._impl.add(other)

    def clear(self) -> None:
        self._impl.clear()

    def __bool__(self) -> bool:
        return bool(self._impl)

    def remove(self, other: _T) -> None:
        return self._impl.remove(other)

    def update(self, other: Iterable[_T]) -> None:
        self._impl.update(other)


# Ignore mypy's incompatible subclass errors.
# We use basedpyright to check this which understands _QuerySetBase properly.
class GroupQuery(_QuerySetBase[Group], base.GroupQuery):  # type: ignore[misc]

    __slots__ = ()

    def _initial(self) -> set[Group]:
        assert self._base.comps
        return {Group(group, self._base) for group in self._base.comps.groups}

    def filter_name(
        self, patterns: base._StrIter, cmp: QueryCmp | int = QueryCmp.EQ, /
    ) -> None:
        _query_update(self, attrgetter("name"), patterns, cmp)

    def filter_groupid(
        self, patterns: base._StrIter, cmp: QueryCmp | int = QueryCmp.EQ, /
    ) -> None:
        _query_update(self, attrgetter("groupid"), patterns, cmp)

    def filter_package_name(
        self, patterns: base._StrIter, cmp: QueryCmp | int = QueryCmp.EQ, /
    ) -> None:
        new: set[Group] = set()
        for group in self:
            if next(
                _query_filter(group.packages, attrgetter("name"), patterns, cmp),
                None,
            ):
                new.add(group)
        self._impl.intersection_update(new)

    # def filter_langonly(self, value: bool) -> None:
    #     _query_update_bool(self, attrgetter("langonly"), value)

    def filter_uservisible(self, value: bool) -> None:
        _query_update_bool(self, attrgetter("uservisible"), value)

    def filterm(self, **kwargs: Unpack[base.GroupQueryKwargs]) -> Self:
        base._filter_func(self, QueryCmp, **kwargs)
        return self


class Environment(base.Environment):
    """
    "Immutable" class representing a comps environment
    """

    __slots__ = ("_impl", "_base")

    def __init__(self, impl: dnf.comps.Environment, base: dnf.Base) -> None:
        self._impl = impl
        self._base = base

    _check_same_base = _check_same_base

    def __hash__(self) -> int:
        return hash(self.environmentid)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Environment):  # pragma: no cover
            return False
        return self.environmentid == other.environmentid and self._base == other._base

    def __gt__(self, other: Environment) -> bool:
        self._check_same_base(other._base)
        return self.environmentid > other.environmentid

    def __ge__(self, other: Environment) -> bool:
        self._check_same_base(other._base)
        return self.environmentid >= other.environmentid

    def __lt__(self, other: Environment) -> bool:
        self._check_same_base(other._base)
        return self.environmentid < other.environmentid

    def __le__(self, other: Environment) -> bool:
        self._check_same_base(other._base)
        return self.environmentid <= other.environmentid

    @property
    def impl(self) -> dnf.comps.Environment:
        return self._impl

    # @property
    # def base(self) -> dnf.Base:
    #     return self._base

    @property
    def environmentid(self) -> str:
        return self._impl.id

    @property
    def name(self) -> str:
        return self._impl.name

    @property
    def description(self) -> str:
        return self._impl.desc

    @property
    def translated_name(self) -> str:
        return self._impl.ui_name

    @property
    def translated_description(self) -> str:
        return self._impl.ui_description

    # TODO: libdnf5 returns strings, not Group objects, so we're not exposing
    # this for now
    # @property
    # def groups(self) -> Sequence[Group]:
    #     return tuple(
    #         Group(group, self._base) for group in self._impl.mandatory_groups)
    #     )
    #
    # @property
    # def optional_groups(self) -> Sequence[Group]:
    #     return tuple(Group(group, self._base) for group in self._impl.optional_groups)

    @property
    def groupids(self) -> Sequence[str]:
        return tuple(group.id for group in self._impl.mandatory_groups)

    @property
    def optional_groupids(self) -> Sequence[str]:
        return tuple(group.id for group in self._impl.optional_groups)


# Ignore mypy's incompatible subclass errors.
# We use basedpyright to check this which understands _QuerySetBase properly.
class EnvironmentQuery(_QuerySetBase[Environment], base.EnvironmentQuery):  # type: ignore[misc]

    __slots__ = ()

    def _initial(self) -> set[Environment]:
        assert self._base.comps
        return {
            Environment(environment, self._base)
            for environment in self._base.comps.environments
        }

    def filter_name(
        self, patterns: base._StrIter, cmp: QueryCmp | int = QueryCmp.EQ, /
    ) -> None:
        _query_update(self, attrgetter("name"), patterns, cmp)

    def filter_environmentid(
        self, patterns: base._StrIter, cmp: QueryCmp | int = QueryCmp.EQ, /
    ) -> None:
        _query_update(self, attrgetter("environmentid"), patterns, cmp)

    def filterm(self, **kwargs: Unpack[base.EnvironmentQueryKwargs]) -> Self:
        base._filter_func(self, QueryCmp, **kwargs)
        return self
