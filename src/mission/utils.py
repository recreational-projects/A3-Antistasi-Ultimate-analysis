"""Mission related."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def _path_looks_like_mission_dir(path: Path) -> bool:
    """
    Verify mission directory candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_mission_dir_path(path)
    return map_name == path.stem[-len(map_name) :].lower()


def mission_dirs_in_dir(path: Path) -> list[Path]:
    """
    Return candidate mission directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    return [p for p in (path.iterdir()) if _path_looks_like_mission_dir(p)]


def map_name_from_mission_dir_path(path: Path) -> str:
    """
    Return map name from mission `path`.

    e.g. `Antistasi_Altis.Altis` -> "altis".
    """
    return path.suffix.lstrip(".").lower()
