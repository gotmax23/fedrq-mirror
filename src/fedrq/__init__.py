# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
fedrq is a tool to query the Fedora and EPEL repositories
"""

from __future__ import annotations

import logging
import os
import warnings

import pydantic

__version__ = "0.15.0.post0"


def _filter_pydantic_v2_warnings() -> None:
    typ: DeprecationWarning | None
    if typ := getattr(pydantic, "PydanticDeprecatedSince20", None):
        warnings.simplefilter(action="ignore", category=typ)


if "_FEDRQ_SHOW_PYDANTIC_WARNINGS" not in os.environ:
    _filter_pydantic_v2_warnings()


fmt = "{levelname}:{name}:{lineno}: {message}"
logging.basicConfig(format=fmt, style="{")
logger = logging.getLogger("fedrq")

__all__ = ("__version__", "logger")
