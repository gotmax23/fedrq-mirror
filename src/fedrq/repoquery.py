# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Provides access to the default package backend interface.
It is recommended to use the backend directly instead of this module.
"""

from __future__ import annotations

from collections.abc import Callable

from fedrq.backends import get_default_backend
from fedrq.backends.base import BaseMakerBase, RepoqueryBase

backend = get_default_backend()
BaseMaker: type[BaseMakerBase] = backend.BaseMaker
Repoquery: type[RepoqueryBase] = backend.Repoquery
get_releasever: Callable[[], str] = backend.get_releasever
BACKEND: str = backend.BACKEND

__all__ = (
    "BACKEND",
    "BaseMaker",
    "Repoquery",
    "backend",
    "get_releasever",
)
