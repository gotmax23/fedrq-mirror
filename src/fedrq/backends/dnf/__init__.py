# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

BACKEND = "dnf"
NEEDS = ("dnf", "hawkey")


def ensure_backend() -> None:
    from fedrq.backends import MissingBackendError

    needs = ", ".join(NEEDS)
    for req in NEEDS:
        if not importlib.util.find_spec(req):
            raise MissingBackendError(f"Backend {BACKEND!r} requires {needs}")


def get_backend() -> ModuleType:
    from . import backend

    return backend
