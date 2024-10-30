# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module (and the other experimental modules in fedrq) are not meant for
public use.
They are subject to breaking changes in minor releases and should not be relied
on by external code.
Once the functionality has stabilized, this code will be moved out of the
experimental namespace.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias, Unpack

_T_co = TypeVar("_T_co", covariant=True)


class SimpleSequence(Protocol[_T_co]):
    """
    Represents a simplified version of the collections.abc.Sequence API that is
    fulfilled by the wrapped C++ vectors in the dnf5 API
    """

    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[_T_co]: ...
    def __getitem__(self, index: int, /) -> _T_co: ...


class GroupPackage(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def package_type(self) -> int: ...
    def __lt__(self, other: Self) -> bool: ...
    def __gt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...
    def __ge__(self, other: Self) -> bool: ...


class Group(Protocol):
    @property
    def groupid(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def translated_name(self) -> str: ...
    @property
    def translated_description(self) -> str: ...
    @property
    def langonly(self) -> bool: ...
    @property
    def uservisible(self) -> bool: ...
    @property
    def packages(self) -> SimpleSequence[GroupPackage]: ...
    def get_packages_of_type(
        self, package_type: int, /
    ) -> SimpleSequence[GroupPackage]: ...
    def __lt__(self, other: Self) -> bool: ...
    def __gt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...
    def __ge__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...


_StrIter: TypeAlias = "list[str] | tuple[str, ...] | str"


class GroupQueryKwargs(TypedDict, total=False):
    groupid: _StrIter
    groupid__eq: _StrIter
    groupid__neq: _StrIter
    groupid__glob: _StrIter
    groupid__contains: _StrIter

    name: _StrIter
    name__eq: _StrIter
    name__neq: _StrIter
    name__glob: _StrIter
    name__contains: _StrIter

    package_name: _StrIter
    package_name__eq: _StrIter
    package_name__neq: _StrIter
    package_name__glob: _StrIter
    package_name__contains: _StrIter

    uservisible: bool

    langonly: bool


class GroupQuery(Protocol):
    def filterm(self, **kwargs: Unpack[GroupQueryKwargs]) -> Self: ...
    def filter_groupid(self, patterns: _StrIter, cmp: int = ..., /) -> None: ...
    def filter_name(self, patterns: _StrIter, cmp: int = ..., /) -> None: ...
    def filter_package_name(self, patterns: _StrIter, cmp: int = ..., /) -> None: ...
    def filter_uservisible(self, value: bool) -> None: ...

    # Not implemented in libdnf5
    # def filter_langonly(self, value: bool) -> None: ...

    # Set methods
    def difference(self, other: Self) -> Self:
        """
        Set difference.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery
        """
        ...

    def union(self, other: Self) -> Self:
        """
        Set union.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery.
        """
        ...

    def intersection(self, other: Self) -> Self:
        """
        Set intersection.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery.
        """
        ...

    def update(self, other: Self) -> None:
        """
        Update set in-place
        """
        ...

    def add(self, other: Group, /) -> None: ...

    def clear(self) -> None: ...

    def __bool__(self) -> bool: ...

    def remove(self, other: Group, /) -> None: ...

    def __contains__(self, other) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Group]: ...
    def __ior__(self, other) -> Self: ...
    def __iand__(self, other) -> Self: ...
    def __isub__(self, other) -> Self: ...


class Environment(Protocol):
    @property
    def environmentid(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def translated_name(self) -> str: ...
    @property
    def translated_description(self) -> str: ...

    # TODO: libdnf5 returns strings, not Group objects, so we're not exposing
    # this for now
    # @property
    # def groups(self) -> SimpleSequence[Group]: ...
    # @property
    # def optional_groups(self) -> SimpleSequence[Group]: ...

    @property
    def groupids(self) -> SimpleSequence[str]: ...
    @property
    def optional_groupids(self) -> SimpleSequence[str]: ...

    def __lt__(self, other: Self) -> bool: ...
    def __gt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...
    def __ge__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...


class EnvironmentQueryKwargs(TypedDict, total=False):
    environmentid: _StrIter
    environmentid__eq: _StrIter
    environmentid__neq: _StrIter
    environmentid__glob: _StrIter
    environmentid__contains: _StrIter

    name: _StrIter
    name__eq: _StrIter
    name__neq: _StrIter
    name__glob: _StrIter
    name__contains: _StrIter


class EnvironmentQuery(Protocol):
    def filterm(self, **kwargs: Unpack[EnvironmentQueryKwargs]) -> Self: ...
    def filter_environmentid(self, patterns: _StrIter, cmp: int = ..., /) -> None: ...
    def filter_name(self, patterns: _StrIter, cmp: int = ..., /) -> None: ...

    # Set methods
    def difference(self, other: Self) -> Self:
        """
        Set difference.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery
        """
        ...

    def union(self, other: Self) -> Self:
        """
        Set union.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery.
        """
        ...

    def intersection(self, other: Self) -> Self:
        """
        Set intersection.
        Depending on the backend, this may change 'self' in place or return a
        new GroupQuery.
        """
        ...

    def update(self, other: Self) -> None:
        """
        Update set in-place
        """
        ...

    def add(self, other: Environment, /) -> None: ...

    def clear(self) -> None: ...

    def __bool__(self) -> bool: ...

    def remove(self, other: Environment, /) -> None: ...

    def __contains__(self, other) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Environment]: ...
    def __ior__(self, other: Self) -> Self: ...
    def __iand__(self, other: Self) -> Self: ...
    def __isub__(self, other: Self) -> Self: ...


def _filter_func(obj: Any, query_cmp_enum: type[Enum], **kwargs: Any):
    cmp_mapping = {member.name.lower(): member.value for member in query_cmp_enum}
    for key, value in kwargs.items():
        func, sep, cmp = key.partition("__")
        if sep and not cmp or cmp and cmp not in cmp_mapping:
            raise ValueError(f"Invalid key: {key}")
        filter_func = getattr(obj, f"filter_{func}")
        if cmp:
            cmp_member = cmp_mapping[cmp]
            filter_func(value, cmp_member)
        else:
            filter_func(value)
