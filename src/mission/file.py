"""File-level utilities."""

import logging
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


def map_name_from_mission_dir_path(path: Path) -> str:
    """
    Return map name from mission `path`.

    e.g. `Antistasi_Altis.Altis` -> "Altis".
    """
    return path.suffix.lstrip(".")


def path_looks_like_mission_dir(path: Path) -> bool:
    """
    Verify mission directory candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_mission_dir_path(path)
    return map_name == path.stem[-len(map_name) :]


def mission_dirs_in_dir(path: Path) -> list[Path]:
    """
    Return candidate maps directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    map_dirs = [p for p in list(path.iterdir()) if path_looks_like_mission_dir(p)]
    log_msg = f"Found {len(map_dirs)} candidate maps in {path}."
    _LOGGER.info(log_msg)
    return map_dirs
