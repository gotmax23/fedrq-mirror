# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
fedrq supports dnf and libdnf5. Importing both in the same process doesn't
work, so we use some finagling to dynmaically load the requested backend.
"""

from __future__ import annotations

import functools
import logging
import warnings
from typing import TYPE_CHECKING

from fedrq.backends import dnf, libdnf5

if TYPE_CHECKING:
    from types import ModuleType

    from .base import BackendMod


class MissingBackendError(Exception):
    pass


BACKENDS: dict[str, ModuleType] = {
    "dnf": dnf,
    "libdnf5": libdnf5,
}
DEFAULT_BACKEND = "dnf"
LOG = logging.getLogger(__name__)


class Backends:
    def __init__(self) -> None:
        self.available: dict[str, ModuleType] = {}
        self.missing: dict[str, MissingBackendError] = {}
        for name, mod in BACKENDS.items():
            try:
                mod.ensure_backend()
            except MissingBackendError as exc:
                self.missing[name] = exc
            else:
                self.available[name] = mod


@functools.lru_cache
def _get_backends() -> Backends:
    return Backends()


class _DefaultBackend:
    def __init__(self) -> None:
        self.backend: BackendMod | None = None

    def __call__(
        self, default: str | None = None, fallback: bool = False
    ) -> BackendMod:
        if not self.backend:
            self.backend = self._get_backend(default, fallback)
            LOG.info("Using %s backend", self.backend.BACKEND)
        elif default and default != self.backend.BACKEND:
            warnings.warn(
                f"Falling back to {self.backend.BACKEND}. {default} cannot be used."
            )
        return self.backend

    def _get_backend(
        self, default: str | None = None, fallback: bool = False
    ) -> BackendMod:
        default = default or DEFAULT_BACKEND
        if default not in BACKENDS:
            raise MissingBackendError(f"Invalid backend {default!r}.")
        backends = _get_backends()
        if backend := backends.available.get(default):
            return backend._get_backend()
        if not fallback:
            raise backends.missing[default]
        if backend := next(iter(backends.available.values()), None):
            return backend._get_backend()
        _split = ", ".join(backends.missing)
        raise MissingBackendError(
            f"Neither of the following backends were available: {_split}"
        )


get_default_backend = _DefaultBackend()
