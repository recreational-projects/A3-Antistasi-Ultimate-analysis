"""Utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"
