# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import os
from functools import cache

from fedrq.backends import get_default_backend
from fedrq.backends.base import BackendMod


@cache
def ensure_default_backend() -> BackendMod:
    backend = os.environ.get("FEDRQ_BACKEND")
    gotten = get_default_backend(backend, bool(backend))
    # Check that get_default_backend does the right thing
    assert (backend or gotten.BACKEND) == gotten.BACKEND
    return gotten
