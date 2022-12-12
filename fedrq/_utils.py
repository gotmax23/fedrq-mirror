# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging
import typing as t

if t.TYPE_CHECKING:
    import dnf
    import hawkey

logger = logging.getLogger(__name__)
# PkgIter = t.Union[hawkey.Query, t.Iterable[dnf.package.Package]]


def get_source_name(package: dnf.package.Package) -> str:
    return package.name if package.arch == "src" else package.source_name


def filter_latest(query: hawkey.Query, latest: t.Optional[int]) -> None:
    logger.debug("filter_latest(query={}, latest={})".format(tuple(query), latest))
    if latest:
        query.filterm(latest=latest)


def mklog(*args: str) -> logging.Logger:
    return logging.getLogger(".".join(args))
