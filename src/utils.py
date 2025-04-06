"""File-level utilities."""

import logging
import tomllib
from pathlib import Path

_CONFIG_FILEPATH = "../scripts/config.toml"
_LOGGER = logging.getLogger(__name__)


def load_config() -> dict[str, str]:
    """Load config."""
    filepath = Path(__file__).resolve().parent / _CONFIG_FILEPATH
    with filepath.open("rb") as fp:
        return tomllib.load(fp)


def map_name_from_path(path: Path) -> str:
    """Return map name from `path`."""
    return path.suffix.lstrip(".")


def path_looks_like_map_dir(path: Path) -> bool:
    """
    Verify map directory_candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_path(path)
    return map_name == path.stem[-len(map_name) :]


def maps_in_dir(path: Path) -> list[Path]:
    """
    Return candidate maps directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    map_dirs = [p for p in list(path.iterdir()) if path_looks_like_map_dir(p)]
    log_msg = f"Found {len(map_dirs)} candidate maps in {path}."
    _LOGGER.info(log_msg)
    return map_dirs
