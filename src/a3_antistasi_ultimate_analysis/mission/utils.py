"""Mission related."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


def pretty_iterable_of_str(iterable: Iterable[str]) -> str:
    """Return e.g. `'a', 'b', 'c'`."""
    return f"'{"', '".join(iterable)}'"


def map_name_from_mission_dir_path(path: Path) -> str:
    """
    Return map name from mission `path`.

    e.g. `Antistasi_Altis.Altis` -> "altis".
    """
    return path.suffix.lstrip(".").lower()
