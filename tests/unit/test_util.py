# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fedrq._utils import exhaust_it


def fake_iter(lst: list[Any]) -> Iterator[None]:
    while lst:
        lst.pop()
        yield


def test_util_exhaust_it():
    lst = [*range(10)]
    exhaust_it(fake_iter(lst))
    assert not lst
