# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
fedrq is a tool to query the Fedora and EPEL repositories
"""

from __future__ import annotations

import logging

__version__ = "0.7.1.post0"

fmt = "{levelname}:{name}:{lineno}: {message}"
logging.basicConfig(format=fmt, style="{")
logger = logging.getLogger("fedrq")
