# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

try:
    import dnf  # noqa
    import hawkey  # noqa
except ImportError:
    HAS_DNF = False
    dnf = None
    hawkey = None
else:
    HAS_DNF = True


def needs_dnf() -> None:
    if not HAS_DNF:
        raise RuntimeError("python3-dnf is not installed.")
