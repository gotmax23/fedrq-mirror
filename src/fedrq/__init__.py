# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import logging

format = "{levelname}:{name}: {message}"
logging.basicConfig(format=format, style="{")
logger = logging.getLogger("fedrq")
