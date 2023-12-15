# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Provides access to the default package backend interface.
It is recommended to use the backend directly instead of this module.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Default to dnf backend for type checking
    from fedrq.backends.dnf import backend
    from fedrq.backends.dnf.backend import (
        BACKEND,
        BaseMaker,
        NEVRAForms,
        Repoquery,
        get_changelogs,
        get_releasever,
    )
else:
    from fedrq.backends import get_default_backend
    from fedrq.backends.base import (
        BackendMod,
        BaseMakerBase,
        NEVRAFormsCompat,
        PackageCompat,
        PackageQueryCompat,
        RepoqueryBase,
        _get_changelogs,
    )

    backend: BackendMod = get_default_backend()
    BaseMaker: type[BaseMakerBase] = backend.BaseMaker
    Package: type[PackageCompat] = backend.Package
    NEVRAForms: type[NEVRAFormsCompat] = backend.NEVRAForms
    PackageQuery: type[PackageQueryCompat] = backend.PackageQuery
    RepoError: type[BaseException] = backend.RepoError
    Repoquery: type[RepoqueryBase] = backend.Repoquery
    get_releasever: Callable[[], str] = backend.get_releasever
    get_changelogs: _get_changelogs = backend.get_changelogs
    BACKEND: str = backend.BACKEND

__all__ = (
    "BACKEND",
    "BaseMaker",
    "NEVRAForms",
    "Repoquery",
    "backend",
    "get_releasever",
    "get_changelogs",
)
