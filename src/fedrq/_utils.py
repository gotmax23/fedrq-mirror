# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging
import typing as t
from collections import deque
from collections.abc import Iterator, MutableMapping

if t.TYPE_CHECKING:
    from fedrq.backends.base import PackageCompat, PackageQueryCompat

logger = logging.getLogger(__name__)


def get_source_name(package: PackageCompat) -> str:
    return package.name if package.arch == "src" else t.cast(str, package.source_name)


def filter_latest(query: PackageQueryCompat, latest: t.Optional[int]) -> None:
    # logger.debug("filter_latest(query={}, latest={})".format(tuple(query), latest))
    if latest:
        query.filterm(latest=latest)


def mklog(*args: str) -> logging.Logger:
    return logging.getLogger(".".join(args))


def merge_dict(
    data: MutableMapping[str, t.Any], dest: MutableMapping[str, t.Any]
) -> None:
    for key, value in tuple(data.items()):
        if key not in dest:
            pass
        elif isinstance(value, MutableMapping) and isinstance(
            dest[key], MutableMapping
        ):
            merge_dict(value, dest[key])
            continue
        dest[key] = value


def exhaust_it(it: Iterator[t.Any]) -> None:
    """
    Exhaust an iterator in the most efficient manner possible
    """
    deque(it, maxlen=0)
