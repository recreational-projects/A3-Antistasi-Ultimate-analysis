"""Define constants and non-core functions used by multiple scripts."""

import logging
import tomllib
from pathlib import Path

from rich.logging import RichHandler

from .mission.utils import map_name_from_mission_dir_path

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure logging in scripts."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )


def require_dir(path: Path) -> None:
    """Require that the path is a directory."""
    if not path.is_dir():
        err_msg = f"No such directory: `{path}` (resolves to `{path.resolve()}`)"
        raise RuntimeError(err_msg)


def _load_config(path: Path) -> dict[str, str]:
    """Load config."""
    with path.open("rb") as fp:
        return tomllib.load(fp)


_BASE_PATH = Path(__file__).resolve().parent
_CONFIG = _load_config(_BASE_PATH.parent / "config.toml")

AU_MAPS_DIRPATH = Path(_CONFIG["AU_SOURCE_DIR_RELATIVE"]) / "A3A/addons/maps"
GRAD_MEH_DIRPATH = Path(_CONFIG["GRAD_MEH_DATA_DIR_RELATIVE"])
DATA_DIRPATH = Path(_CONFIG["INTERMEDIATE_DATA_DIR_RELATIVE"])
DOC_DIRPATH = Path(_CONFIG["MARKDOWN_OUTPUT_DIR_RELATIVE"])


def mission_dirs_in_dir(path: Path) -> list[Path]:
    """
    Return candidate mission directories from a directory.

    Arguments:
        path: Directory to be searched.

    Returns:
        List of `Path`s.

    """
    return [p for p in (path.iterdir()) if _path_looks_like_mission_dir(p)]


def _path_looks_like_mission_dir(path: Path) -> bool:
    """
    Verify mission directory candidate.

    Return True if `path` is a directory with name pattern `...{string}.{string}`.
    """
    if not path.is_dir():
        return False

    map_name = map_name_from_mission_dir_path(path)
    return map_name == path.stem[-len(map_name) :].lower()
