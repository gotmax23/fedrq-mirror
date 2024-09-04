"""
Typing stub for basedypright to ignore all types for RPM module
"""

from __future__ import annotations

from typing import Any

def __getattr__(attr: str) -> Any:
    return ...
