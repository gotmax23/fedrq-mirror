# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

# ruff: noqa: E402

"""
Test dnf-specific backend code
"""

from __future__ import annotations

from typing import Any

import pytest
from typing_extensions import Self

from tests import ensure_default_backend

default_backend = ensure_default_backend()

if default_backend.BACKEND != "dnf":
    pytest.skip("This test checks dnf functionality", allow_module_level=True)

import dnf

from fedrq.backends.dnf.backend.experimental import (
    QueryCmp,
    _query_update,
    _QuerySetBase,
)
from fedrq.backends.dnf.backend.experimental import base as experimental_base


def test_bm_set_var_invalid():
    bm = default_backend.BaseMaker()
    with pytest.raises(KeyError, match="best is not a valid substitution"):
        bm.set_var("best", "")


class _QuerySetTest(_QuerySetBase[str]):
    def _initial(self) -> set[str]:
        return set(map(str, range(10)))

    def filter_num(
        self, patterns: experimental_base._StrIter, cmp: int | QueryCmp = QueryCmp.EQ
    ) -> None:
        _query_update(self, lambda x: x, patterns, cmp)

    def filterm(self, **kwargs: Any) -> Self:
        experimental_base._filter_func(self, QueryCmp, **kwargs)
        return self


def test_query_set() -> None:
    base = dnf.Base()
    query_set = _QuerySetTest(base=base)
    query_set2 = _QuerySetTest(base=base)
    assert len(query_set) == 10
    assert "9" in query_set
    assert next(iter(sorted(query_set))) == "0"
    query_set2.filterm(num__eq="8")
    assert list(query_set2) == ["8"]
    assert list(query_set.union(query_set2)) == list(query_set)
    assert list(query_set.intersection(query_set2)) == list(query_set2)
    assert "8" not in (query_set.difference(query_set2))

    orig_query_set = sorted(query_set)
    query_set |= query_set2
    assert sorted(query_set) == orig_query_set

    query_set = _QuerySetTest(base)
    query_set &= query_set2
    assert sorted(query_set) == sorted(query_set2)

    query_set = _QuerySetTest(base)
    query_set -= query_set2
    assert "8" not in query_set

    query_set.clear()
    query_set.add("10")
    assert "10" in query_set
