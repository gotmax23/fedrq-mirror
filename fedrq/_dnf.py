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
